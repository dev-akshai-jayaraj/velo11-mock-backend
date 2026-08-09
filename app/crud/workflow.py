from pathlib import Path

from app.core.config import settings
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)

system_module = CsvRepository("system_modules", _DATA_DIR)
approval_workflow = CsvRepository("approval_workflows", _DATA_DIR)
approval_stage = CsvRepository("approval_stages", _DATA_DIR)
approval_stage_approver = CsvRepository("approval_stage_approvers", _DATA_DIR)
approval_request = CsvRepository("approval_requests", _DATA_DIR)
approval_action = CsvRepository("approval_actions", _DATA_DIR)
