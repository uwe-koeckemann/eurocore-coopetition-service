import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from euro_core_backend.main import app, get_session

from euro_core_backend.test import test_entry_a, test_entry_b, test_team_a, test_team_b, test_league


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_module_usage(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    offer_team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    consumer_team_id = client.post("/entry/create/", json=test_team_b).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    offer_id = client.post("/module-offer/create", json={
        "team_id": offer_team_id,
        "module_id": module_id,
        "royalty": 1000}).json()["id"]
    league_entry_id = client.post("/entry/create/", json=test_league).json()["id"]
    task_id = client.post("/task/create/", json={
        "league_id": league_entry_id,
        "task_seq_nr": 1,
        "name": "Task 1"
    }).json()["id"]
    milestone_id = client.post("/milestone/create/", json={
        "league_id": league_entry_id,
        "task_id": task_id,
        "name": "Milestone 1",
        "points": 10
    }).json()["id"]
    response = client.post("/module-usage/create", json={
        "consumer_team_id": consumer_team_id,
        "module_offer_id": offer_id,
        "milestone_id": milestone_id,
    })

    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["consumer_team_id"] == consumer_team_id
    assert data["module_offer_id"] == offer_id
    assert data["milestone_id"] == milestone_id


def test_get_module_usage(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    offer_team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    consumer_team_id = client.post("/entry/create/", json=test_team_b).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    offer_id = client.post("/module-offer/create", json={
        "team_id": offer_team_id,
        "module_id": module_id,
        "royalty": 1000}).json()["id"]
    league_entry_id = client.post("/entry/create/", json=test_league).json()["id"]
    task_id = client.post("/task/create/", json={
        "league_id": league_entry_id,
        "task_seq_nr": 1,
        "name": "Task 1"
    }).json()["id"]
    milestone_id = client.post("/milestone/create/", json={
        "league_id": league_entry_id,
        "task_id": task_id,
        "name": "Milestone 1",
        "points": 10
    }).json()["id"]
    response = client.post("/module-usage/create", json={
        "consumer_team_id": consumer_team_id,
        "module_offer_id": offer_id,
        "milestone_id": milestone_id,
    })
    response_get = client.get(f"/module-usage/get/{response.json()['id']}")
    app.dependency_overrides.clear()
    data = response_get.json()
    assert response_get.status_code == 200
    assert data["consumer_team_id"] == consumer_team_id
    assert data["module_offer_id"] == offer_id
    assert data["milestone_id"] == milestone_id


def test_get_module_usage_id_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get(f"/module-usage/get/{-1}")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_get_module_usage_all_empty(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get(f"/module-usage/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == []


def test_get_module_offer_get_all_results(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    offer_team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    consumer_team_id = client.post("/entry/create/", json=test_team_b).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    offer_id = client.post("/module-offer/create", json={
        "team_id": offer_team_id,
        "module_id": module_id,
        "royalty": 1000}).json()["id"]
    league_entry_id = client.post("/entry/create/", json=test_league).json()["id"]
    task_id = client.post("/task/create/", json={
        "league_id": league_entry_id,
        "task_seq_nr": 1,
        "name": "Task 1"
    }).json()["id"]
    milestone_id = client.post("/milestone/create/", json={
        "league_id": league_entry_id,
        "task_id": task_id,
        "name": "Milestone 1",
        "points": 10
    }).json()["id"]
    client.post("/module-usage/create", json={
        "consumer_team_id": consumer_team_id,
        "module_offer_id": offer_id,
        "milestone_id": milestone_id,
    })

    response = client.get(f"/module-usage/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_module_usage_update_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.put("/module-usage/update", json={"tokens": 100})
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_module_usage_update_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    offer_team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    consumer_team_id = client.post("/entry/create/", json=test_team_b).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    offer_id = client.post("/module-offer/create", json={
        "team_id": offer_team_id,
        "module_id": module_id,
        "royalty": 1000}).json()["id"]
    league_entry_id = client.post("/entry/create/", json=test_league).json()["id"]
    task_id = client.post("/task/create/", json={
        "league_id": league_entry_id,
        "task_seq_nr": 1,
        "name": "Task 1"
    }).json()["id"]
    milestone_id = client.post("/milestone/create/", json={
        "league_id": league_entry_id,
        "task_id": task_id,
        "name": "Milestone 1",
        "points": 10
    }).json()["id"]
    current = client.post("/module-usage/create", json={
        "consumer_team_id": consumer_team_id,
        "module_offer_id": offer_id,
        "milestone_id": milestone_id,
    }).json()
    current["milestone_id"] = -1
    response_update = client.put("/module-usage/update", json=current)
    response_get = client.get(f"/module-usage/get/{current['id']}")

    app.dependency_overrides.clear()
    data = response_get.json()
    assert response_update.status_code == 200
    assert data["consumer_team_id"] == consumer_team_id
    assert data["module_offer_id"] == offer_id
    assert data["milestone_id"] == -1


def test_module_usage_delete_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.delete("/module-usage/delete/1")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_module_usage_delete_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    offer_team_id = client.post("/entry/create/", json=test_team_a).json()['id']
    consumer_team_id = client.post("/entry/create/", json=test_team_b).json()['id']
    module_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    offer_id = client.post("/module-offer/create", json={
        "team_id": offer_team_id,
        "module_id": module_id,
        "royalty": 1000}).json()["id"]
    league_entry_id = client.post("/entry/create/", json=test_league).json()["id"]
    task_id = client.post("/task/create/", json={
        "league_id": league_entry_id,
        "task_seq_nr": 1,
        "name": "Task 1"
    }).json()["id"]
    milestone_id = client.post("/milestone/create/", json={
        "league_id": league_entry_id,
        "task_id": task_id,
        "name": "Milestone 1",
        "points": 10
    }).json()["id"]
    usage_id = client.post("/module-usage/create", json={
        "consumer_team_id": consumer_team_id,
        "module_offer_id": offer_id,
        "milestone_id": milestone_id,
    }).json()["id"]

    response_get_before = client.get(f"/module-usage/get/{usage_id}")
    response_delete = client.delete(f"/module-usage/delete/{usage_id}")
    response_get_after = client.get(f"/module-usage/get/{usage_id}")
    app.dependency_overrides.clear()
    assert response_get_before.status_code == 200
    assert response_delete.status_code == 200
    assert response_get_after.status_code == 404
