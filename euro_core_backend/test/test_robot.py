import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from euro_core_backend.main import app, get_session

from euro_core_backend.test import test_entry_a
from euro_core_backend.test import test_entry_b


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_robot(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.post("/relation-type/create", json={
        "name": "uses",
        "inverse_name": "used_by",
        "topic": "1",
        "inverse_topic": "2",
        "description": "3",
    })
    assert response.status_code == 200
    client.post("/relation-type/create", json={
        "name": "supports",
        "inverse_name": "supported_by",
        "topic": "1",
        "inverse_topic": "2",
        "description": "3",
    })
    client.post("/relation-type/create", json={
        "name": "part_of",
        "inverse_name": "has_part",
        "topic": "1",
        "inverse_topic": "2",
        "description": "3",
    })
    user_1_id = client.post("/entry/create", json={
        "name": "User 1", "url": "user", "description": "DESC"}).json()["id"]
    user_2_id = client.post("/entry/create", json={
        "name": "User 2", "url": "user", "description": "DESC"}).json()["id"]
    hw_1_id = client.post("/entry/create", json={
        "name": "HW 1", "url": "user", "description": "DESC"}).json()["id"]
    hw_2_id = client.post("/entry/create", json={
        "name": "HW 2", "url": "user", "description": "DESC"}).json()["id"]
    mod_1_id = client.post("/entry/create", json={
        "name": "Module 1", "url": "user", "description": "DESC"}).json()["id"]
    mod_2_id = client.post("/entry/create", json={
        "name": "Module 2", "url": "user", "description": "DESC"}).json()["id"]
    response = client.post("/robot/create", json={
        "name": "Robot 1",
        "url": "URL",
        "description": "DESC",
        "user_ids": [user_1_id, user_2_id],
        "hardware_ids": [hw_1_id, hw_2_id],
        "module_ids": [mod_1_id, mod_2_id],
    })
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Robot 1"
    assert data["url"] == "URL"
    assert data["description"] == "DESC"
    assert data["id"] is not None
    assert data["user_ids"] == [user_1_id, user_2_id]
    assert data["hardware_ids"] == [hw_1_id, hw_2_id]
    assert data["module_ids"] == [mod_1_id, mod_2_id]


def test_get_entry_by_id(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response_post = client.post("/entry/create", json=test_entry_a)
    entry_id = response_post.json()["id"]

    response = client.get(
        f"/entry/get/{entry_id}"
    )
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Entry_A"
    assert data["url"] == "URL"
    assert data["description"] == "DESC"
    assert data["id"] == entry_id


def test_get_entry_by_id_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.get("/entry/get/-1")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_get_entry_by_name(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response_post = client.post("/entry/create", json=test_entry_a)
    entry_id = response_post.json()["id"]
    response = client.get("/entry/get-by-name/Entry_A")
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Entry_A"
    assert data["url"] == "URL"
    assert data["description"] == "DESC"
    assert data["id"] == entry_id


def test_get_entry_by_name_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.get(f"/entry/get-by-name/Entry_Not_In_DB")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_get_entry_get_all_empty(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.get(f"/entry/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == []


def test_get_entry_get_all_two_results(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    client.post("/entry/create", json=test_entry_a)
    client.post("/entry/create", json=test_entry_b)

    response = client.get(f"/entry/get-all")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_entry_update_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.put("/entry/update", json={"name": "New_Name"})
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_entry_update_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response_create = client.post("/entry/create", json=test_entry_a)
    entry_current = response_create.json()
    entry_current["name"] = "New_Name"
    response_update = client.put("/entry/update", json=entry_current)

    response_get = client.get(f"/entry/get/{entry_current['id']}")
    app.dependency_overrides.clear()
    assert response_update.status_code == 200
    assert response_update.json()["name"] == "New_Name"
    assert response_get.json()["name"] == "New_Name"


def test_entry_delete_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.delete("/entry/delete/1")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_entry_delete_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response_create = client.post("/entry/create", json=test_entry_a)
    entry_current = response_create.json()
    response_get_before = client.get(f"/entry/get/{entry_current['id']}")
    response_delete = client.delete(f"/entry/delete/{entry_current['id']}")
    response_after = client.get(f"/entry/get/{entry_current['id']}")

    app.dependency_overrides.clear()
    assert response_get_before.status_code == 200
    assert response_delete.status_code == 200
    assert response_after.status_code == 404


def test_entry_tag(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    entry_id = client.post("/entry/create", json=test_entry_a).json()["id"]
    tag_a_id = client.post("/tag/create", json={"name": "A"}).json()["id"]
    tag_b_id = client.post("/tag/create", json={"name": "B"}).json()["id"]

    add_tag_a_response = client.post(f"/entry/add-tag/{entry_id}/{tag_a_id}")
    add_tag_b_response = client.post(f"/entry/add-tag/{entry_id}/{tag_b_id}")
    get_tags_response = client.get(f"/entry/get-tags/{entry_id}")
    app.dependency_overrides.clear()

    assert add_tag_a_response.status_code == 200
    assert add_tag_b_response.status_code == 200
    assert get_tags_response.status_code == 200
    assert len(get_tags_response.json()) == 2


def test_entry_get_tags_failure(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    get_tags_response = client.get(f"/entry/get-tags/1")
    app.dependency_overrides.clear()
    assert get_tags_response.status_code == 404
