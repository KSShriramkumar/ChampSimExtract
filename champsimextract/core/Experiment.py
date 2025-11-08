from dataclasses import dataclass
from champsimextract.core.ChampsimLog import ChampsimLogCollection
from champsimextract.core.metrics import Metric
from champsimextract.plotting import plotter
from champsimextract.misc.MetricAggr import MetricAggregator 

@dataclass
class Configuration:
    name: str
    logCollection: ChampsimLogCollection

    def __init__(self, name: str, logdir: str,get_workload_name_from_path, get_simpoint_from_path):
        self.name = name
        self.logCollection = ChampsimLogCollection(log_dir=logdir)
        self.get_workload_name_from_path = get_workload_name_from_path
        self.get_simpoint_from_path = get_simpoint_from_path
    def get_data_dict(self, metric: Metric) -> dict:
        data = {}
        for log in self.logCollection.logs:
            if self.get_workload_name_from_path(log.path) not in data:
                data[self.get_workload_name_from_path(log.path)] = {}
            if self.get_simpoint_from_path(log.path) not in data:
                data[self.get_workload_name_from_path(log.path)][self.get_simpoint_from_path(log.path)] = None
            data[self.get_workload_name_from_path(log.path)][self.get_simpoint_from_path(log.path)] = metric.get_val(log)
        return data

@dataclass
class Experiment:
    name: str
    configurations: list[Configuration]

    def __init__(self, name: str, configurations: dict[str, str],get_workload_name_from_path, get_simpoint_from_path):
        self.name = name
        self.configurations = []
        for config_name, logdir in configurations.items():
            config = Configuration(name=config_name, logdir=logdir, get_workload_name_from_path=get_workload_name_from_path, get_simpoint_from_path=get_simpoint_from_path)
            self.configurations.append(config)
    
    def get_data_dict(self,metric:Metric) -> dict:
        data = {}

        for config in self.configurations:
            data[config.name] = config.get_data_dict(metric)

        return data
    
    def get_reduced_data_dict(self, metric: Metric, aggregator: MetricAggregator) -> dict:
        data = self.get_data_dict(metric)
        data = aggregator.reduce_data(data)
        return data

    def get_reduced_data_dict_with_avg(self,metric: Metric, aggregator: MetricAggregator) -> dict:
        data = self.get_data_dict(metric)
        data = aggregator.add_avg(data)
        return data
    
    def plot(self, metric: Metric, aggregator: MetricAggregator, plot_type: str="bar",**plot_kwargs):
        data = self.get_reduced_data_dict(metric, aggregator)
        plot = plotter.Plotter(data, **plot_kwargs)
        if plot_type == "bar":
            plot.plot_multi_bar()
        elif plot_type == "stacked":
            plot.plot_stacked_bar()
        elif plot_type == "line":
            plot.plot_line()
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")
    
    def __str__(self) -> str:
        return f"Experiment(name={self.name}, num_configurations={len(self.configurations)})"

