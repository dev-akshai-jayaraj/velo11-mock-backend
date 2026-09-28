from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

player_match_stat = CsvRepository("player_match_stats", _DATA_DIR)
team_match_stat = CsvRepository("team_match_stats", _DATA_DIR)
player_season_stat = CsvRepository("player_season_stats", _DATA_DIR)
team_season_stat = CsvRepository("team_season_stats", _DATA_DIR)
