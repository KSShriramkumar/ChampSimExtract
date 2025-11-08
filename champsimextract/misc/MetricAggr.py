from typing import Dict
import copy

def average(values: list) -> float:
    return sum(values) / len(values) if values else 0.0
class MetricAggregator:
    def __init__(self, reducer=None, name: str="average"):
        if not reducer:
            reducer = average
        self.reducer = reducer
        self.name = name

    def reduce_data(self,data: Dict[str, Dict[str, Dict[str, float]]]):
        reduction  = {}
        for conf, workload_dict in data.items():
            for workload,simpoint_dict in workload_dict.items():
                simpoint_values = list(simpoint_dict.values())
                avg_value = self.reducer(simpoint_values)
                if conf not in reduction:
                    reduction[conf] = {}
                reduction[conf][workload] = avg_value
        return reduction
    
    def add_avg(self, data: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        reduction = self.reduce_data(data)
        reduction_with_avg = copy.deepcopy(reduction)
        for conf, workload_dict in reduction.items():
            conf_vals = list(workload_dict.values())
            reduction_with_avg[conf][self.name] = self.reducer(conf_vals) if self.reducer else sum(conf_vals)/len(conf_vals)
        return reduction_with_avg

