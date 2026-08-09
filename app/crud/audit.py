from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

audit_log = CsvRepository("audit_logs", _DATA_DIR)
