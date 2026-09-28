from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

team_dynamics_assessment = CsvRepository("team_dynamics_assessments", _DATA_DIR)
player_relationship = CsvRepository("player_relationships", _DATA_DIR)
unit_cohesion = CsvRepository("unit_cohesion", _DATA_DIR)
