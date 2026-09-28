from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

player = CsvRepository("players", _DATA_DIR)
team_player = CsvRepository("team_players", _DATA_DIR)
player_availability = CsvRepository("player_availability", _DATA_DIR)
