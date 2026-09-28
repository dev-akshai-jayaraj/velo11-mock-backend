from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

scouting_note = CsvRepository("scouting_notes", _DATA_DIR)
opposition_analysis = CsvRepository("opposition_analyses", _DATA_DIR)
tactical_plan = CsvRepository("tactical_plans", _DATA_DIR)
set_piece_plan = CsvRepository("set_piece_plans", _DATA_DIR)
