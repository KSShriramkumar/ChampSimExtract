import logging
import sys
from pathlib import Path
from typing import Optional, Union

LogLevel = Union[int, str]
logging.getLogger("matplotlib").setLevel(logging.WARNING)
def setup_logging(
    *,
    level: LogLevel = "WARNING",
    log_file: Optional[str] = None,
) -> None:
    """
    Configure global logging.

    Defaults:
      - level: WARNING
      - output: stdout

    Args:
        level: Logging level (e.g. "INFO", "DEBUG", logging.INFO)
        log_file: If provided, log to this file path instead of stdout
    """

    # Normalize level
    if isinstance(level, str):
        level = level.upper()

    handler: logging.Handler

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(path)
    else:
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
setup_logging()

