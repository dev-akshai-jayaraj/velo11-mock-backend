from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

season = CsvRepository("seasons", _DATA_DIR)
competition = CsvRepository("competitions", _DATA_DIR)
player_position = CsvRepository("player_positions", _DATA_DIR)
competition_season = CsvRepository("competition_seasons", _DATA_DIR)
team_competition = CsvRepository("team_competitions", _DATA_DIR)
