from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

home_club = CsvRepository("home_clubs", _DATA_DIR)
venue = CsvRepository("venues", _DATA_DIR)
own_team = CsvRepository("own_teams", _DATA_DIR)
