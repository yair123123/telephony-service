from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.dependencies import get_core_client
from app.main import app


class DummyCoreClient:
    async def resolve_call_route(self, phone: str):
        raise NotImplementedError

    async def process_call_order(self, payload):
        raise NotImplementedError

    async def confirm_ride(self, ride_id):
        return {"ok": True}

    async def cancel_searching_by_customer_phone(self, phone):
        return {"ok": True}


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db_url = "sqlite:///./test_telephony.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    dummy = DummyCoreClient()

    def override_db():
        try:
            yield db_session
        finally:
            pass

    from app.db.session import get_db_session

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_core_client] = lambda: dummy
    with TestClient(app) as test_client:
        yield test_client, dummy
    app.dependency_overrides.clear()
