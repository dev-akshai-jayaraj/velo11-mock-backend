from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

data_source = CsvRepository("data_sources", _DATA_DIR)
data_import = CsvRepository("data_imports", _DATA_DIR)
