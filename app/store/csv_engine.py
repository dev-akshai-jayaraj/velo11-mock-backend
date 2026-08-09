"""Low-level CSV read/write: type coercion in and out of on-disk string cells.

Locking is intentionally exposed (get_lock) rather than done inside read/write
here, because callers that need read-modify-write atomicity (CsvRepository)
must hold one lock across the whole sequence, not one lock per call.
"""

import csv
import json
import threading
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.store.registry import EntitySpec, FieldType

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def get_lock(path: Path) -> threading.Lock:
    key = str(path)
    with _locks_guard:
        if key not in _locks:
            _locks[key] = threading.Lock()
        return _locks[key]


def _serialize(value: Any, ftype: FieldType) -> str:
    if value is None:
        return ""
    if ftype == FieldType.JSON:
        return json.dumps(value)
    if ftype == FieldType.BOOL:
        return "true" if value else "false"
    return str(value)


def _deserialize(raw: str | None, ftype: FieldType) -> Any:
    if raw is None or raw == "":
        return None
    if ftype == FieldType.STR:
        return raw
    if ftype == FieldType.INT:
        return int(raw)
    if ftype == FieldType.BOOL:
        return raw.strip().lower() in ("true", "1", "yes")
    if ftype == FieldType.UUID:
        return uuid.UUID(raw)
    if ftype == FieldType.DATETIME:
        return datetime.fromisoformat(raw)
    if ftype == FieldType.DATE:
        return date.fromisoformat(raw)
    if ftype == FieldType.JSON:
        return json.loads(raw)
    raise ValueError(f"Unknown field type: {ftype}")


def read_rows_unlocked(path: Path, spec: EntitySpec) -> list[dict[str, Any]]:
    """Read and type-coerce every row. Caller must hold get_lock(path) first."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        raw_rows = list(csv.DictReader(f))
    type_map = {fld.name: fld.type for fld in spec.fields}
    return [
        {name: _deserialize(row.get(name), ftype) for name, ftype in type_map.items()}
        for row in raw_rows
    ]


def write_rows_unlocked(path: Path, spec: EntitySpec, rows: list[dict[str, Any]]) -> None:
    """Overwrite the file with the given rows. Caller must hold get_lock(path) first."""
    type_map = {fld.name: fld.type for fld in spec.fields}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=spec.fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {name: _serialize(row.get(name), ftype) for name, ftype in type_map.items()}
            )
    tmp_path.replace(path)
