import uuid
from typing import Literal

from fastapi import APIRouter, Query, Request, status

from app.core.errors import NOT_FOUND, AppError
from app.schemas.common import APIResponse
from app.store.repository import CsvRepository

# Query params consumed by the list endpoint itself; everything else on the
# querystring is treated as an exact-match filter against a CSV column.
_RESERVED_QUERY_PARAMS = {"skip", "limit", "sort_by", "sort_order"}


def build_crud_router(
    *,
    crud: CsvRepository,
    read_schema: type,
    create_schema: type,
    update_schema: type | None = None,
    prefix: str,
    tags: list[str],
) -> APIRouter:
    """Wire up standard list/create/get/update/delete REST endpoints for a resource.

    Backed by CsvRepository (flat CSV files), not a database — see app/store/.
    Every endpoint responds with the common envelope: {status, message, result, error}.
    """

    router = APIRouter(prefix=prefix, tags=tags)
    resource = tags[0]
    singular = resource[:-1] if resource.endswith("s") else resource

    @router.get(
        "/", response_model=APIResponse[list[read_schema]], summary=f"List {resource}"
    )
    def list_items(
        request: Request,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = Query(None, description="Column name to sort by"),
        sort_order: Literal["asc", "desc"] = "asc",
    ):
        filters = {
            k: v for k, v in request.query_params.items() if k not in _RESERVED_QUERY_PARAMS
        }
        items = crud.list(
            skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order, filters=filters
        )
        return APIResponse[list[read_schema]].ok(
            message=f"{resource} fetched successfully", result=items
        )

    @router.post(
        "/",
        response_model=APIResponse[read_schema],
        status_code=status.HTTP_201_CREATED,
        summary=f"Create {singular}",
    )
    def create_item(obj_in: create_schema):  # type: ignore[valid-type]
        obj = crud.create(obj_in.model_dump())
        return APIResponse[read_schema].ok(
            message=f"{singular} created successfully", result=obj
        )

    @router.get(
        "/{item_id}", response_model=APIResponse[read_schema], summary=f"Get {singular}"
    )
    def get_item(item_id: uuid.UUID):
        obj = crud.get(item_id)
        if obj is None:
            raise AppError(
                status_code=status.HTTP_404_NOT_FOUND,
                code=NOT_FOUND,
                message=f"{singular} not found",
            )
        return APIResponse[read_schema].ok(
            message=f"{singular} fetched successfully", result=obj
        )

    if update_schema is not None:

        @router.patch(
            "/{item_id}",
            response_model=APIResponse[read_schema],
            summary=f"Update {singular}",
        )
        def update_item(item_id: uuid.UUID, obj_in: update_schema):  # type: ignore[valid-type]
            existing = crud.get(item_id)
            if existing is None:
                raise AppError(
                    status_code=status.HTTP_404_NOT_FOUND,
                    code=NOT_FOUND,
                    message=f"{singular} not found",
                )
            updated = crud.update(item_id, obj_in.model_dump(exclude_unset=True))
            return APIResponse[read_schema].ok(
                message=f"{singular} updated successfully", result=updated
            )

    @router.delete(
        "/{item_id}", response_model=APIResponse[None], summary=f"Delete {singular}"
    )
    def delete_item(item_id: uuid.UUID):
        existing = crud.get(item_id)
        if existing is None:
            raise AppError(
                status_code=status.HTTP_404_NOT_FOUND,
                code=NOT_FOUND,
                message=f"{singular} not found",
            )
        crud.remove(item_id)
        return APIResponse[None].ok(message=f"{singular} deleted successfully")

    return router
