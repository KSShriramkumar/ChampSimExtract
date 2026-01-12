import pathlib
from champsimextract.core.traces import Trace   
from typing import List
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChampsimLog:
    path: pathlib.Path
    traces: List[Trace]
    is_valid_log: bool

    def __init__(self, logpath: pathlib.Path):
        """Parse a ChampSim log file to extract all trace paths."""
        
        self.traces = []
        self.path = pathlib.Path(logpath)
        trace_regex = re.compile(r"CPU\s+(\d+)\s+runs\s+(.+)")
        simulation_completed_regex = re.compile(r"ChampSim completed all CPUs")
        log_file = pathlib.Path(logpath)

        with log_file.open('r') as f:
            for line in f:
                trace_path_match = trace_regex.match(line.strip())
                simulation_completed_match = simulation_completed_regex.match(line.strip())
                if trace_path_match:
                    cpu_id = int(trace_path_match.group(1))
                    assert(cpu_id == len(self.traces))
                    trace_path = pathlib.Path(trace_path_match.group(2)).resolve()
                    self.traces.append(Trace(trace_path))
                    logger.debug(f"ChampsimLog created for log at {self.path} for traces {self.traces}")
                if simulation_completed_match:
                    self.is_valid_log = True
                    return
                
    
        logger.warning(f"Valid simulation not found in log path {log_file}")
        self.is_valid_log = False

    def get_log_text(self) -> str:
        with self.path.open('r') as f:
            return f.read()
@dataclass
class ChampsimLogCollection:
    path: pathlib.Path
    logs: List[ChampsimLog]

    def __init__(self, log_dir: str):
        self.path = pathlib.Path(log_dir)
        self.logs = []
        for root,_,files in self.path.walk():
            if(len(files) == 0):
                logger.warning(f"{root} has no logs")
            for file in files:
                log_path = pathlib.Path(root)/file
                log_object = ChampsimLog(logpath=log_path)
                if log_object.is_valid_log:
                    self.logs.append(log_object)
        if(len(self.logs) == 0):
            logger.warning(f"ChampsimLogCollection at {self.path} initialised with 0 logs")
        logger.debug(f"ChampsimLogCollection created for logs at {self.path} number of logs = {len(self.logs)}")
        
    
    def __str__(self) -> str:
        return f"ChampsimLogCollection(path={self.path}, num_logs={len(self.logs)})"
    
    def __repr__(self) -> str:
        return f"ChampsimLogCollection(path={self.path}, num_logs={len(self.logs)})"