import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional
from matplotlib.ticker import FormatStrFormatter, MaxNLocator


class Plotter:
    def __init__(
        self,
        data: Dict[str, Dict[str, float]],
        rounding: int = 2,
        base_color: str = "gray",
        bar_width: float = 0.25,
        font_size: int = 10,
        rotation: int = 45,
        legend_loc: str = "best",
        avg_key: str = "__avg__",
        round_to: float = 0.05,
        delta_round: float = 0.01,
        delta_factor: float = 1.0,
        color_map: Optional[Dict[str, str]] = None,
        ylabel: str = "",
        title: str = "",
    ):
        """
        Generic plotter supporting multi-bar, stacked, and line plots.
        Data format: data[config][workload] = value
        """
        self.data = data
        self.rounding = rounding
        self.bar_width = bar_width
        self.font_size = font_size
        self.rotation = rotation
        self.legend_loc = legend_loc
        self.avg_key = avg_key
        self.round_to = round_to
        self.delta_round = delta_round
        self.delta_factor = delta_factor
        self.color_map = color_map
        self.ylabel = ylabel
        self.title = title
        # Extract configs and workloads
        self.configs = list(data.keys())
        self.workloads = list(next(iter(data.values())).keys())
        self.workloads_sorted = self._sorted_workloads()

        # Build numeric matrix
        self.values = np.array([
            [data[conf][wl] for wl in self.workloads_sorted]
            for conf in self.configs
        ])

        # Generate colors (grayscale or user-defined)
        self.colors = self._generate_colors(base_color, len(self.configs))

        # Compute y-axis limits
        self._ymin, self._ymax, self._delta = self._compute_yaxis_limits()

    # ---------- Helpers ----------

    def _sorted_workloads(self) -> List[str]:
        avg_present = any(w.lower() == self.avg_key.lower() for w in self.workloads)
        sorted_wls = sorted([w for w in self.workloads if w.lower() != self.avg_key.lower()], key=str.lower)
        if avg_present:
            sorted_wls.append(self.avg_key)
        return sorted_wls

    def _generate_colors(self, base: str, n: int):
        if self.color_map:
            return [self.color_map.get(conf, str(0.2 + 0.6 * (i / max(1, n - 1)))) for i, conf in enumerate(self.configs)]
        return [str(0.2 + 0.6 * (i / max(1, n - 1))) for i in range(n)]

    def _compute_yaxis_limits(self):
        maximum = np.max(self.values)
        minimum = np.min(self.values)
        tick_count = 10
        delta = int(((maximum - minimum) / tick_count) / self.delta_round) * self.delta_round * self.delta_factor
        ymin = max(0, int(minimum / self.round_to) * self.round_to)
        ymax = maximum + delta
        return ymin, ymax, delta

    def _setup_plot(self, ylabel: str, title: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_ylabel(ylabel, fontsize=self.font_size)
        if title:
            ax.set_title(title, fontsize=self.font_size + 2)
        ax.set_xticks(range(len(self.workloads_sorted)))
        ax.set_xticklabels(self.workloads_sorted, rotation=self.rotation, ha="right", fontsize=self.font_size)
        ax.yaxis.set_major_formatter(FormatStrFormatter(f'%.{self.rounding}f'))
        ax.yaxis.set_major_locator(MaxNLocator(integer=False))
        ax.set_ylim(self._ymin, self._ymax)
        ax.set_yticks(np.arange(self._ymin, self._ymax + self._delta, self._delta))
        return fig, ax

    def _finalize_plot(self, ax, title: Optional[str] = None):
        ax.legend(fontsize=self.font_size - 1, loc=self.legend_loc)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        if title:
            ax.set_title(title)
        plt.tight_layout()

    # ---------- Plot types ----------

    def plot_multi_bar(self):
        fig, ax = self._setup_plot(self.ylabel, self.title)
        x = np.arange(len(self.workloads_sorted))
        for i, conf in enumerate(self.configs):
            offset = (i - len(self.configs) / 2) * self.bar_width + self.bar_width / 2
            ax.bar(x + offset, self.values[i], width=self.bar_width,
                   color=self.colors[i], label=conf)
        self._finalize_plot(ax, self.title)
        plt.show()

    def plot_stacked_bar(self):
        fig, ax = self._setup_plot(self.ylabel, self.title)
        x = np.arange(len(self.workloads_sorted))
        bottom = np.zeros(len(self.workloads_sorted))
        for i, conf in enumerate(self.configs):
            ax.bar(x, self.values[i], bottom=bottom,
                   color=self.colors[i], label=conf)
            bottom += self.values[i]
        self._finalize_plot(ax, self.title)
        plt.show()

    def plot_line(self):
        fig, ax = self._setup_plot(self.ylabel, self.title)
        x = np.arange(len(self.workloads_sorted))
        for i, conf in enumerate(self.configs):
            ax.plot(x, self.values[i], marker='o', color=self.colors[i],
                    label=conf, linewidth=2)
        self._finalize_plot(ax, self.title)
        plt.show()
