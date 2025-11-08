from __future__ import annotations
import re
from champsimextract.core.ChampsimLog import ChampsimLog
class Metric:
    def __init__(self,name:str,regex_pattern:str) -> None:
        self.pattern = re.compile(regex_pattern)
        self.name = name
    def get_val(self,log:ChampsimLog):
        raise NotImplementedError("Subclasses must implement get_val method")

class BaseMetric(Metric):
    '''A base metric defined by a regex pattern to extract a value from a Champsim log.'''
    def __init__(self,name:str,regex_pattern:str) -> None:
        self.pattern = re.compile(regex_pattern)
        self.name = name
    def get_val(self,log:ChampsimLog):
        match = self.pattern.search(log.get_log_text())
        if not match:
            raise ValueError(f"Metric pattern {self.name} did not match log {log.path}")
        elif len(match.groups()) > 1:
            raise ValueError(f"Metric pattern {self.name} has more than one capturing group in log {log.path}")
        elif len(match.groups()) == 1:
            return match.groups()[0]
        return None

class CustomMetric(Metric):
    '''A metric defined by multiple base metrics and a processing function.
    The processing function takes as input the raw values extracted by each base metric
    and returns the final value of the custom metric. The order of metrics in the list and processing
    function arguments must match.'''
    def __init__(self,metrics:list[BaseMetric],process_func) -> None:
        self.metrics = metrics
        self.process_func = process_func
    def get_val(self,log:ChampsimLog):
        raw_values = [metric.get_val(log) for metric in self.metrics]
        return self.process_func(*raw_values)

    
class BaselinedMetric(Metric):
    '''A metric that computes the ratio of a base metric between two configurations.
    Defaults to current / baseline, but a custom normalisation function can be provided.
    It is assumed that the log name structure is the same between the two configurations.'''
    is_cross_config = True
    def __init__(self,name,base_metric:Metric,baseline_config:"Configuration",normalisation_func=None) -> None:
        self.name=name
        self.base_metric = base_metric
        self.baseline_config_data = baseline_config.get_data_dict(base_metric)
        self.baseline_config = baseline_config
        if normalisation_func is None:
            self.normalisation_func = lambda current, baseline: current / baseline
        else:
            self.normalisation_func = normalisation_func
    def get_val(self,log:ChampsimLog):
        current_value = float(self.base_metric.get_val(log))
        baseline_value = float(self.baseline_config_data\
                               [self.baseline_config.get_workload_name_from_path(log.path)]\
                               [self.baseline_config.get_simpoint_from_path(log.path)])
        if baseline_value == 0:
            raise ValueError(f"Baseline value for config {self.baseline_config.name} is zero, cannot compute baselined metric.")
        return self.normalisation_func(current_value,baseline_value)