import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.security import hash_password
from app.store.repository import CsvRepository

_DATA_DIR = Path(settings.DATA_DIR)


class UserCsvRepository(CsvRepository):
    """Same CSV repository behavior, but never persists a plaintext password."""

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        data = dict(data)
        password = data.pop("password")
        data["password_hash"] = hash_password(password)
        return super().create(data)

    def update(self, item_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        data = dict(data)
        password = data.pop("password", None)
        if password is not None:
            data["password_hash"] = hash_password(password)
        return super().update(item_id, data)


user = UserCsvRepository("users", _DATA_DIR)
role = CsvRepository("roles", _DATA_DIR)
permission = CsvRepository("permissions", _DATA_DIR)
user_role = CsvRepository("user_roles", _DATA_DIR)
role_permission = CsvRepository("role_permissions", _DATA_DIR)
