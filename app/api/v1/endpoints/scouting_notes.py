from app.api.router_factory import build_crud_router
from app.crud.preparation import scouting_note
from app.schemas.preparation import ScoutingNoteCreate, ScoutingNoteRead, ScoutingNoteUpdate

router = build_crud_router(
    crud=scouting_note,
    read_schema=ScoutingNoteRead,
    create_schema=ScoutingNoteCreate,
    update_schema=ScoutingNoteUpdate,
    prefix="/scouting-notes",
    tags=["Scouting Notes"],
)
