import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from champsimextract.core import *
from champsimextract.misc.MetricAggr import MetricAggregator

def geometric_mean(values):
    product = 1.0
    n = len(values)
    for v in values:
        product *= v
    return product ** (1.0 / n)
if __name__ == "__main__":
    ipc = BaseMetric(
        name="IPC",
        regex_pattern=r"CPU \d+ cumulative IPC:\s+([0-9]*\.[0-9]+).*"
    )
    speedup = BaselinedMetric(
        name="Speedup",
        base_metric=ipc,
        baseline_config=Configuration(
            name="ConfigB",
            logdir="/mnt/d/CODE/RnD/results/LLC-Size/4096",
            get_workload_name_from_path=lambda path: path.name.split('_')[2],
            get_simpoint_from_path=lambda path: path.name.split('_')[0]
        )
    )
    exp = Experiment(
        name="Sample Experiment",
        configurations={
            "ConfigA": "/mnt/d/CODE/RnD/results/LLC-Size/8192",
            "ConfigB": "/mnt/d/CODE/RnD/results/LLC-Size/4096"
        },
        get_workload_name_from_path=lambda path: path.name.split('_')[2],
        get_simpoint_from_path=lambda path: path.name.split('_')[0]
    )
    for config in exp.configurations:
        print(f"Configuration: {config.name}, Number of Logs: {len(config.logCollection.logs)}")
    agg = MetricAggregator(reducer=geometric_mean)
    print(exp.plot(speedup, agg, plot_type="bar", title="Speedup Bar Plot", ylabel="Speedup", base_color="blue", round_to=0.1,delta_round=0.01, delta_factor=1,color_map={"ConfigA":"red","ConfigB":"green"}))


