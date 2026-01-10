import pathlib
from champsimextract.core.traces import Trace   
from typing import List
from dataclasses import dataclass
import re
import logging
from champsimextract.common.logging import setup_logging
setup_logging(logging.DEBUG)

logger = logging.getLogger(__name__)

@dataclass
class ChampsimLog:
    path: pathlib.Path
    traces: List[Trace]

    def __init__(self, logpath: pathlib.Path):
        """Parse a ChampSim log file to extract all trace paths."""
        
        self.traces = []
        self.path = pathlib.Path(logpath)
        pattern = re.compile(r"CPU\s+(\d+)\s+runs\s+(.+)")
        log_file = pathlib.Path(logpath)

        with log_file.open('r') as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    cpu_id = int(match.group(1))
                    assert(cpu_id == len(self.traces))
                    trace_path = pathlib.Path(match.group(2)).resolve()
                    self.traces.append(Trace(trace_path))
        logging.debug(f"ChampsimLog created for log at {self.path} for traces {self.traces}")
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
            for file in files:
                log_path = pathlib.Path(root)/file
                self.logs.append(ChampsimLog(logpath=log_path))
        logging.debug(f"ChampsimLogCollection created for logs at {self.path} number of logs = {len(self.logs)}")
        
    
    def __str__(self) -> str:
        return f"ChampsimLogCollection(path={self.path}, num_logs={len(self.logs)})"
    
    def __repr__(self) -> str:
        return f"ChampsimLogCollection(path={self.path}, num_logs={len(self.logs)})"