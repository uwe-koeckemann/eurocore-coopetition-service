import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from euro_core_backend.main import app, get_session

from euro_core_backend.test import test_entry_a, test_entry_b, test_league


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_team_tokens(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    team_entry_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    league_entry_id = client.post("/entry/create/", json=test_league).json()['id']
    response = client.post("/team-tokens/create", json={
        "team_id": team_entry_id,
        "league_id": league_entry_id,
        'points': 0
    })
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["team_id"] == team_entry_id
    assert data["league_id"] == league_entry_id
    assert data["points"] == 0


def test_get_team_tokens(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_entry_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    league_entry_id = client.post("/entry/create/", json=test_league).json()['id']
    client.post("/team-tokens/create", json={
        "team_id": team_entry_id,
        "league_id": league_entry_id,
        'points': 10
    })

    response = client.get(f"/team-tokens/get/{team_entry_id}/{league_entry_id}")
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["team_id"] == team_entry_id
    assert data["league_id"] == league_entry_id
    assert data["points"] == 10



def test_get_team_tokens_by_id_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get(f"/team-tokens/get/{-1}")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_get_team_tokens_all_empty(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get(f"/team-tokens/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == []


def test_get_team_tokens_get_all_two_results(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_a_entry_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    team_b_entry_id = client.post("/entry/create/", json=test_entry_b).json()['id']

    league_entry_id = client.post("/entry/create/", json=test_league).json()['id']
    client.post("/team-tokens/create", json={
        "team_id": team_a_entry_id,
        "league_id": league_entry_id,
        'points': 10
    })
    client.post("/team-tokens/create", json={
        "team_id": team_b_entry_id,
        "league_id": league_entry_id,
        'points': 5
    })


    response = client.get(f"/team-tokens/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_team_tokens_update_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.put("/tag/update", json={"tokens": 100})
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_team_tokens_update_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_entry_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    league_entry_id = client.post("/entry/create/", json=test_league).json()['id']
    current_tokens = client.post("/team-tokens/create", json={
        "team_id": team_entry_id,
        "league_id": league_entry_id,
        'points': 10
    }).json()
    current_tokens["points"] = 15
    response_update = client.put("/team-tokens/update", json=current_tokens)
    response_get = client.get(f"/team-tokens/get/{team_entry_id}/{league_entry_id}")

    app.dependency_overrides.clear()
    assert response_update.status_code == 200
    assert response_update.json()["points"] == 15
    assert response_get.json()["points"] == 15



def test_team_tokens_delete_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.delete("/tag/delete/1")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_team_tokens_delete_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    team_entry_id = client.post("/entry/create/", json=test_entry_a).json()['id']
    league_entry_id = client.post("/entry/create/", json=test_league).json()['id']
    current_tokens = client.post("/team-tokens/create", json={
        "team_id": team_entry_id,
        "league_id": league_entry_id,
        'points': 10
    }).json()
    response_get_before = client.get(f"/team-tokens/get/{team_entry_id}/{league_entry_id}")
    response_delete = client.delete(f"/team-tokens/delete/{team_entry_id}/{league_entry_id}")
    response_after = client.get(f"/team-tokens/get/{team_entry_id}/{league_entry_id}")

    app.dependency_overrides.clear()
    assert response_get_before.status_code == 200
    assert response_delete.status_code == 200
    assert response_after.status_code == 404

