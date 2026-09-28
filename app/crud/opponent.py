from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

opponent_club = CsvRepository("opponent_clubs", _DATA_DIR)
opponent_team = CsvRepository("opponent_teams", _DATA_DIR)
