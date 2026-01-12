import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional
from matplotlib.ticker import FormatStrFormatter, MaxNLocator
import matplotlib.colors as mcolors
import colorsys

YTICK_COUNT=10 # MUST BE POSITIVE
class Plotter:
    def __init__(
        self,
        data: Dict[str, Dict[str, float]],
        kind:str='bar',
        ytick_rounding: int = 2,
        base_color: str = "gray",
        font_size: int = 22,
        ytick_font_size: int = 16,  
        rotation: int = 60,
        legend_loc: str = "best",
        avg_key: str = "__avg__",
        round_to: float = 0.05,
        delta_round: float = 0.01,
        delta_factor: float = 1.0,
        color_map: Optional[Dict[str, str]] = None,
        ylabel: str = "",
        border_weight: float = 1.5,
        title: str = "",
        tune_yticks: bool = False
    ):
        """
        Generic plotter supporting multi-bar, stacked, and line plots.
        Data format: data[config][workload] = value
        """
        self.data = data
        self.kind = kind
        self.ytick_rounding = ytick_rounding
        self.font_size = font_size
        self.ytick_font_size = ytick_font_size
        self.rotation = rotation
        self.legend_loc = legend_loc
        self.avg_key = avg_key
        self.round_to = round_to
        self.delta_round = delta_round
        self.delta_factor = delta_factor
        self.color_map = color_map
        self.ylabel = ylabel
        self.border_weight = border_weight
        self.title = title
        self.tune_yticks = tune_yticks
        if self.title != '':
            raise ValueError("Title not implemented yet")
        # Extract configs and workloads
        assert(delta_factor > 0, "Delta factor must be positive")
        assert(delta_round !=0, "Delta round must be positive")

        self.configs = list(data.keys())
        self.workloads = list(next(iter(data.values())).keys())
        self.workloads_sorted = self._sorted_workloads()
        self.bar_width = min(min(0.3,0.8/ len(self.configs)),len(self.workloads)*(0.04))

        assert(self.bar_width > 0, "Bar width must be positive")
        # Build numeric matrix
        self.values = np.array([
            [data[conf][wl] for wl in self.workloads_sorted]
            for conf in self.configs
        ])
        
        # Generate colors (grayscale or user-defined)
        self.colors = self._generate_colors(base_color, len(self.configs))

        # Compute y-axis limits
        self._ymin, self._ymax, self._delta = self._compute_yaxis_limits(self.kind)

    # ---------- Helpers ----------

    def _sorted_workloads(self) -> List[str]:
        """ Sort workloads alphabetically, placing avg_key at the end if present. """
        avg_present = any(w.lower() == self.avg_key.lower() for w in self.workloads)
        sorted_wls = sorted([w for w in self.workloads if w.lower() != self.avg_key.lower()], key=str.lower)
        if avg_present:
            sorted_wls.append(self.avg_key)
        
        return sorted_wls

    def _generate_colors(self, base: str, n: int):
        """
        Generate n shades from very light base color to the base color itself
        using HLS for better perceptual scaling.
        """
        if self.color_map:
            return [self.color_map.get(conf, base) for conf in self.configs]

        # Convert base color to RGB
        base_rgb = mcolors.to_rgb(base)
        h, l, s = colorsys.rgb_to_hls(*base_rgb)

        # Define lightest and darkest lightness
        lightest = min(1.0, l + (0.5 if base == 'gray'  else  0.3))  # very light (but <=1)
        darkest = max(0, l - (0.3 if base == 'gray'  else  0.15) )     # darker than base

        lightness_scale = np.linspace(lightest, darkest, n)

        shades = []
        for li in lightness_scale:
            shade_rgb = colorsys.hls_to_rgb(h, li, s)
            shades.append(mcolors.to_hex(shade_rgb))
        return shades
    def _compute_yaxis_limits(self, kind: str):
        """
        Compute y-axis limits and tick delta for plotting.

        Parameters:
            kind (str): 'stacked' or any other kind of plot.

        Returns:
            ymin (int): Minimum y-axis value (usually 0).
            ymax (float): Maximum y-axis value.
            delta (float): Tick step for y-axis.
        """
        if kind == "stacked":
            # Sum across the stacking dimension (axis=1)
            maximum = np.max(np.sum(self.values, axis=0))
            minimum = np.min(self.values) # stacked bars usually start at 0
        else:
            maximum = np.max(self.values)
            minimum = np.min(self.values)

        tick_count = YTICK_COUNT
        # Compute a rounded delta for ticks
        delta = int(((maximum - minimum) / tick_count) / self.delta_round) * self.delta_round * self.delta_factor
        ymin = max(0, int(minimum / self.round_to) * self.round_to)
        ymax = maximum + delta
        
        if self.tune_yticks:
            # Adjust ymax to be a multiple of delta
            print("Delta factor: ",self.delta_factor)
            print("Delta round: ",self.delta_round)
            print("Delta: ",delta)
            print("Round to: ",self.round_to)
            print("Ymin: ",ymin)
            print("Ymax: ",ymax)


        return ymin, ymax, delta


    def _setup_plot(self, ylabel: str,title: Optional[str] = None):
        """
        Set up the plot with labels, ticks, and limits.
        Returns:
            fig, ax: Matplotlib figure and axis objects.
        """
        fig, ax = plt.subplots(figsize=(12, 6),constrained_layout=True)
        for spine in ax.spines.values():
            spine.set_zorder(10)
            spine.set_edgecolor('black')  # Set color of the border
            spine.set_linewidth(self.border_weight)  #
        ax.set_ylabel(ylabel, fontsize=self.font_size)
        if title:
            ax.set_title(title, fontsize=self.font_size + 2)
        ax.set_xticks(range(len(self.workloads_sorted)))
        ax.set_xticklabels(self.workloads_sorted, rotation=self.rotation, ha="center", fontsize=self.font_size)
        ax.yaxis.set_major_formatter(FormatStrFormatter(f'%.{self.ytick_rounding}f'))
        ax.yaxis.set_major_locator(MaxNLocator(integer=False))
        ax.set_ylim(self._ymin, self._ymax)
        ax.set_yticks(np.arange(self._ymin, self._ymax, self._delta))
        
        ax.tick_params(axis='y', labelsize=self.ytick_font_size, labelcolor='black')

        
        return fig, ax

    def _finalize_plot(self, ax,fig, title: Optional[str] = None):
        """ Finalize the plot with legend and grid.
        """
        legend = ax.legend(loc='center',bbox_to_anchor=(0.5,1.15), ncol=len(self.configs),fontsize=self.font_size-2,edgecolor='black',fancybox=False, bbox_transform=ax.transAxes)
        legend.get_frame().set_linewidth(self.border_weight)
        ax.grid(axis="y", linestyle="--", alpha=0.5,zorder=1)
        if title:
            ax.set_title(title)
        plt.tight_layout()

    # ---------- Plot types ----------

    def plot_multi_bar(self,savepath: str = ""):
        """ Plot multi-bar chart.
        """
        fig, ax = self._setup_plot(self.ylabel, self.title)
        x = np.arange(len(self.workloads_sorted))
        for i, conf in enumerate(self.configs):
            offset = (i - len(self.configs) / 2) * self.bar_width + self.bar_width / 2
            ax.bar(x + offset, self.values[i], width=self.bar_width,
                   color=self.colors[i], label=conf, edgecolor='black', linewidth=self.border_weight,zorder=5)
        self._finalize_plot(ax,fig, self.title)
        
        if savepath != "":
            plt.savefig(savepath)
            plt.close()
            return
        plt.show()

    def plot_stacked_bar(self,savepath: str = ""):
        """ Plot stacked bar chart.
        """
        fig, ax = self._setup_plot(self.ylabel, self.title)
        x = np.arange(len(self.workloads_sorted))
        bottom = np.zeros(len(self.workloads_sorted))
        for i, conf in enumerate(self.configs):
            ax.bar(x, self.values[i], bottom=bottom,
                   color=self.colors[i], label=conf, edgecolor='black', linewidth=self.border_weight,zorder=5)
            bottom += self.values[i]
        self._finalize_plot(ax,fig, self.title)
        if savepath != "":
            plt.savefig(savepath)
            plt.close()
            return
        plt.show()

    def plot_line(self,savepath: str = ""):
        """ Plot line chart.
        """
        fig, ax = self._setup_plot(self.ylabel, self.title)
        x = np.arange(len(self.workloads_sorted))
        for i, conf in enumerate(self.configs):
            ax.plot(x, self.values[i], marker='o', color=self.colors[i],
                    label=conf, linewidth=2)
        self._finalize_plot(ax,fig, self.title)
        if savepath != "":
            plt.savefig(savepath)
            plt.close()
            return
        plt.show()
    
    ### ---------- Master plot ---------- ###
    def plot(self,savepath: str = ""):
        """ Master plot function to select plot type. Saves to file if savepath is provided. See individual plot methods for details.
        """
        if self.kind == "bar":
            self.plot_multi_bar(savepath=savepath)
        elif self.kind == "stacked":
            self.plot_stacked_bar(savepath=savepath)
        elif self.kind == "line":
            self.plot_line(savepath=savepath)
        else:
            raise ValueError(f"Unknown plot type: {self.kind}")
    