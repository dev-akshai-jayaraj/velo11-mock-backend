"""Generic CSV-backed repository: mimics the DB CRUD/sort/filter surface the
routers already expect, plus the referential-integrity checks a real database
would otherwise enforce for us (FK existence, unique constraints, restrict-on-delete).
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import status

from app.core.errors import CONFLICT, INVALID_REFERENCE, AppError
from app.store import csv_engine
from app.store.registry import REGISTRY, EntitySpec


class CsvRepository:
    def __init__(self, entity_name: str, data_dir: Path):
        self.entity_name = entity_name
        self.spec: EntitySpec = REGISTRY[entity_name]
        self.data_dir = data_dir
        self.path = data_dir / self.spec.csv_file
        self.lock = csv_engine.get_lock(self.path)

    # -- internal helpers ---------------------------------------------------

    def _read_all(self) -> list[dict[str, Any]]:
        return csv_engine.read_rows_unlocked(self.path, self.spec)

    def _write_all(self, rows: list[dict[str, Any]]) -> None:
        csv_engine.write_rows_unlocked(self.path, self.spec, rows)

    def _read_other(self, other_spec: EntitySpec) -> list[dict[str, Any]]:
        other_path = self.data_dir / other_spec.csv_file
        return csv_engine.read_rows_unlocked(other_path, other_spec)

    def _check_unique(
        self, rows: list[dict[str, Any]], candidate: dict[str, Any], *, exclude_id: uuid.UUID | None = None
    ) -> None:
        for combo in self.spec.unique:
            values = {f: candidate.get(f) for f in combo}
            for row in rows:
                if exclude_id is not None and row["id"] == exclude_id:
                    continue
                if all(row.get(f) == v for f, v in values.items()):
                    fields = ", ".join(combo)
                    raise AppError(
                        status_code=status.HTTP_409_CONFLICT,
                        code=CONFLICT,
                        message=f"A {self.entity_name} record with the same {fields} already exists.",
                    )

    def _check_fk(self, candidate: dict[str, Any]) -> None:
        for fld in self.spec.fk_fields:
            if fld.name not in candidate:
                continue
            value = candidate[fld.name]
            if value is None:
                continue
            target_spec = REGISTRY[fld.fk]
            target_rows = self._read_other(target_spec)
            if not any(row["id"] == value for row in target_rows):
                raise AppError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=INVALID_REFERENCE,
                    message=f"'{fld.name}' references a {fld.fk} record that does not exist.",
                )

    def _check_not_referenced(self, item_id: uuid.UUID) -> None:
        for other_name, other_spec in REGISTRY.items():
            referencing_fields = [f.name for f in other_spec.fk_fields if f.fk == self.entity_name]
            if not referencing_fields:
                continue
            other_rows = self._read_other(other_spec)
            for row in other_rows:
                if any(row.get(fname) == item_id for fname in referencing_fields):
                    raise AppError(
                        status_code=status.HTTP_409_CONFLICT,
                        code=CONFLICT,
                        message=f"Cannot delete: this {self.entity_name} record is still referenced by a {other_name} record.",
                    )

    # -- public API -----------------------------------------------------------

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        with self.lock:
            rows = self._read_all()

        if filters:
            unknown = [k for k in filters if k not in self.spec.fieldnames]
            if unknown:
                raise AppError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="INVALID_FILTER_FIELD",
                    message=f"Cannot filter by unknown field(s): {', '.join(unknown)}",
                )
            rows = [
                row
                for row in rows
                if all(_stringify(row.get(k)).lower() == v.lower() for k, v in filters.items())
            ]

        if sort_by:
            if sort_by not in self.spec.fieldnames:
                raise AppError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="INVALID_SORT_FIELD",
                    message=f"Cannot sort by unknown field '{sort_by}'.",
                )
            reverse = sort_order.lower() == "desc"
            # (is_none, value) tuples never compare None against a real value: when both
            # rows are non-None the first element ties and Python falls through to compare
            # the values; when either is None the first element alone decides the order.
            rows = sorted(
                rows,
                key=lambda r: (r.get(sort_by) is None, r.get(sort_by)),
                reverse=reverse,
            )

        return rows[skip : skip + limit]

    def get(self, item_id: uuid.UUID) -> dict[str, Any] | None:
        with self.lock:
            rows = self._read_all()
        return next((r for r in rows if r["id"] == item_id), None)

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            rows = self._read_all()
            self._check_fk(data)

            new_row: dict[str, Any] = dict.fromkeys(self.spec.fieldnames)
            new_row.update(data)
            new_row["id"] = uuid.uuid4()
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            for field_name in self.spec.auto_now_add_fields:
                if new_row.get(field_name) is None:
                    new_row[field_name] = now

            self._check_unique(rows, new_row)
            rows.append(new_row)
            self._write_all(rows)
        return new_row

    def update(self, item_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        with self.lock:
            rows = self._read_all()
            idx = next((i for i, r in enumerate(rows) if r["id"] == item_id), None)
            if idx is None:
                return None

            self._check_fk(data)
            merged = {**rows[idx], **data}
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            for field_name in self.spec.auto_now_fields:
                merged[field_name] = now

            self._check_unique(rows, merged, exclude_id=item_id)
            rows[idx] = merged
            self._write_all(rows)
        return merged

    def remove(self, item_id: uuid.UUID) -> bool:
        with self.lock:
            rows = self._read_all()
            idx = next((i for i, r in enumerate(rows) if r["id"] == item_id), None)
            if idx is None:
                return False
            self._check_not_referenced(item_id)
            rows.pop(idx)
            self._write_all(rows)
        return True


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
