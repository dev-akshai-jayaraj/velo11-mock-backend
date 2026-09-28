from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

analytics_snapshot = CsvRepository("analytics_snapshots", _DATA_DIR)
recommendation = CsvRepository("recommendations", _DATA_DIR)
report = CsvRepository("reports", _DATA_DIR)
