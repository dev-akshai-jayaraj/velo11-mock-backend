from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

fixture = CsvRepository("fixtures", _DATA_DIR)
match = CsvRepository("matches", _DATA_DIR)
match_context = CsvRepository("match_contexts", _DATA_DIR)
match_lineup = CsvRepository("match_lineups", _DATA_DIR)
match_lineup_player = CsvRepository("match_lineup_players", _DATA_DIR)
match_event = CsvRepository("match_events", _DATA_DIR)
