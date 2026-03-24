from fastapi import FastAPI

from app.api.routes.dtmf import router as dtmf_router
from app.api.routes.health import router as health_router
from app.api.routes.incoming_call import router as incoming_router
from app.api.routes.recordings import router as recordings_router
from app.config import get_settings
from app.db.base import Base
from app.db.models import call_event_model, call_recording_model, call_session_model  # noqa: F401
from app.db.session import engine
from app.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(health_router)
app.include_router(incoming_router)
app.include_router(recordings_router)
app.include_router(dtmf_router)
