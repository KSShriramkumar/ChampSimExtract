import pathlib
from dataclasses import dataclass

@dataclass
class Trace:
    path: pathlib.Path

@dataclass
class TraceCollection:
    path: pathlib.Path
    traces: list[Trace]
    
    def __init__(self,tracedir: str):
        self.path = pathlib.Path(tracedir)
        self.traces = []
        for root,_,files in self.path.walk():
            for file in files:
                if not (file.endswith(".xz") or file.endswith(".gz")):
                    raise ValueError(f"Unsupported trace file format: {file}")
                trace_path = pathlib.Path(root)/file
                self.traces.append(Trace(path=trace_path))