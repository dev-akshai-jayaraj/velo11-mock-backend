from app.api.router_factory import build_crud_router
from app.crud.preparation import set_piece_plan
from app.schemas.preparation import SetPiecePlanCreate, SetPiecePlanRead, SetPiecePlanUpdate

router = build_crud_router(
    crud=set_piece_plan,
    read_schema=SetPiecePlanRead,
    create_schema=SetPiecePlanCreate,
    update_schema=SetPiecePlanUpdate,
    prefix="/set-piece-plans",
    tags=["Set Piece Plans"],
)
