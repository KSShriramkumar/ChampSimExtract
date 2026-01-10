from champsimextract.core import *
from champsimextract.misc.MetricAggr import MetricAggregator
from champsimextract.common.metrics import LLC_LOAD_MPKI
from champsimextract.common.aggregators import GEOMEAN
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

def flat_split_list(parts:list,sep):
    """Splits a list of strings by a separator and flattens the result into a single list."""
    result = []
    for part in parts:
        result.extend(part.split(sep))
    return result

def flat_split_multi_sep(inp_str:str,sep:list[str]):
    """Splits a list of strings by a separator and flattens the result into a single list. 
    Splits based on list of seperators"""
    result = inp_str.split(sep[0])
    for s in sep[1:]:
        result = flat_split_list(result,s)
    return result

if __name__ == "__main__":
   
    exp = Experiment(
        name="Sample Experiment",
        configurations={
            "8MB": os.path.join(BASE_DIR,"../data/LLC-Size/8192"),
            "16MB": os.path.join(BASE_DIR,"../data/LLC-Size/16384"),
            "32MB": os.path.join(BASE_DIR,"../data/LLC-Size/32768"),
        },
        get_workload_name_from_log_filename=lambda path: flat_split_multi_sep(path.name,sep=['.','-','_'])[2],
        get_simpoint_from_log_filename=lambda path: flat_split_multi_sep(path.name,sep=['.','-','_'])[3]
    )
    for config in exp.configurations:
        print(f"Configuration: {config.name}, Number of Logs: {len(config.logCollection.logs)}")
    
    
    exp.plot(LLC_LOAD_MPKI, GEOMEAN,savepath="temp.pdf",plot_type="bar", ylabel="Speedup",tune_yticks=True,base_color="orange" ,round_to=1,delta_round=1, delta_factor=2,ytick_rounding=0)
    exp.print_table(LLC_LOAD_MPKI, GEOMEAN,latex=True)
    
