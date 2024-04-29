import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from euro_core_backend.main import app, get_session

from euro_core_backend.test import test_entry_a, test_entry_b, test_team_a


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_module_offer(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    response = client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_id,
        "royalty": 1000,
    })

    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["team_id"] == team_id
    assert data["module_id"] == module_id
    assert data["royalty"] == 1000


def test_create_module_offer_with_defaults(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    response = client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_id,
        "royalty": 100
    })

    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["team_id"] == team_id
    assert data["module_id"] == module_id
    assert data["royalty"] == 100


def test_get_module_offer(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    response_create = client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_id,
        "royalty": 100
    })
    response_get = client.get(f"/module-offer/get/{response_create.json()['id']}")
    app.dependency_overrides.clear()
    data = response_get.json()
    assert response_get.status_code == 200
    assert data["royalty"] == 100


def test_get_module_offer_by_id_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get(f"/module-offer/get/{-1}")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_get_module_offer_all_empty(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get(f"/module-offer/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == []


def test_get_module_offer_get_all_two_results(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    module_a_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    module_b_id = client.post("/entry/create/", json=test_entry_b).json()['id']
    client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_a_id,
        "royalty": 1000
    })
    client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_b_id,
        "royalty": 100
    })

    response = client.get(f"/module-offer/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_module_offer_update_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.put("/module-offer/update", json={"tokens": 100})
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_module_offer_update_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    current = client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_id,
        "royalty": 100
    }).json()
    current["royalty"] = 299
    response_update = client.put("/module-offer/update", json=current)
    response_get = client.get(f"/module-offer/get/{current['id']}")

    app.dependency_overrides.clear()
    assert response_update.status_code == 200
    assert response_update.json()["royalty"] == 299
    assert response_get.json()["royalty"] == 299


def test_module_offer_delete_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.delete("/module-offer/delete/1")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_module_offer_delete_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    offer_id = client.post("/module-offer/create", json={
        "team_id": team_id,
        "module_id": module_id,
        "royalty": 100
    }).json()["id"]
    response_get_before = client.get(f"/module-offer/get/{offer_id}")
    response_delete = client.delete(f"/module-offer/delete/{offer_id}")
    response_get_after = client.get(f"/module-offer/get/{offer_id}")
    app.dependency_overrides.clear()
    assert response_get_before.status_code == 200
    assert response_delete.status_code == 200
    assert response_get_after.status_code == 404
