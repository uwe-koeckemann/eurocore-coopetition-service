import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from euro_core_backend.main import app, get_session
from euro_core_backend.relation_query import RelationQuery

from euro_core_backend.test import test_relation_a
from euro_core_backend.test import test_relation_b
from euro_core_backend.test import test_entry_a
from euro_core_backend.test import test_entry_b
from euro_core_backend.helpers import get_entry_relations


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.post('/relation/create/1/2/3')
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_create_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    id_from = client.post("/entry/create", json=test_entry_a).json()['id']
    id_to = client.post("/entry/create", json=test_entry_b).json()['id']
    rel_type = client.post("/relation_type/create", json=test_relation_a).json()['id']

    response = client.post(f"/relation/create/{rel_type}/{id_from}/{id_to}")
    app.dependency_overrides.clear()
    assert response.status_code == 200


def test_delete_fails(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    response = client.delete("/relation/delete/1/2/3")
    app.dependency_overrides.clear()
    assert response.status_code == 404


def test_delete_succeeds(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    id_from = client.post("/entry/create", json=test_entry_a).json()['id']
    id_to = client.post("/entry/create", json=test_entry_b).json()['id']
    rel_type = client.post("/relation_type/create", json=test_relation_a).json()['id']
    client.post(f"/relation/create/{rel_type}/{id_from}/{id_to}")
    response_get_a = client.get(f"/relation/get-by-type/{rel_type}")
    response = client.delete(f"/relation/delete/{rel_type}/{id_from}/{id_to}")
    response_get_b = client.get(f"/relation/get-by-type/{rel_type}")
    app.dependency_overrides.clear()

    assert len(response_get_a.json()) == 1
    assert len(response_get_b.json()) == 0
    assert response.status_code == 200


def test_get_incoming(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    id_from = client.post("/entry/create", json=test_entry_a).json()['id']
    id_to = client.post("/entry/create", json=test_entry_b).json()['id']
    rel_type_a = client.post("/relation_type/create", json=test_relation_a).json()['id']
    rel_type_b = client.post("/relation_type/create", json=test_relation_b).json()['id']
    client.post(f"/relation/create/{rel_type_a}/{id_from}/{id_to}")
    client.post(f"/relation/create/{rel_type_b}/{id_from}/{id_to}")

    response_get_type_a = client.get(f"/relation/get-by-type/{rel_type_a}")
    response_get_type_b = client.get(f"/relation/get-by-type/{rel_type_a}")
    response_get_in_a = client.get(f"/relation/get-incoming/{id_from}")
    response_get_in_b = client.get(f"/relation/get-incoming/{id_to}")
    response_get_out_a = client.get(f"/relation/get-outgoing/{id_from}")
    response_get_out_b = client.get(f"/relation/get-outgoing/{id_to}")

    app.dependency_overrides.clear()

    assert len(response_get_type_a.json()) == 1
    assert len(response_get_type_b.json()) == 1
    assert len(response_get_in_a.json()) == 0
    assert len(response_get_in_b.json()) == 2
    assert len(response_get_out_a.json()) == 2
    assert len(response_get_out_b.json()) == 0

    assert response_get_type_a.status_code == 200
    assert response_get_type_b.status_code == 200
    assert response_get_in_a.status_code == 200
    assert response_get_in_b.status_code == 200
    assert response_get_out_a.status_code == 200
    assert response_get_out_b.status_code == 200


def test_relation_query_same_category(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    id_from = client.post("/entry/create", json=test_entry_a).json()['id']
    id_to = client.post("/entry/create", json=test_entry_b).json()['id']
    rel_type_a = client.post("/relation_type/create", json=test_relation_a).json()['id']
    rel_type_b = client.post("/relation_type/create", json=test_relation_b).json()['id']
    client.post(f"/relation/create/{rel_type_a}/{id_from}/{id_to}")
    client.post(f"/relation/create/{rel_type_b}/{id_to}/{id_from}")

    tag_a_id = client.post("/tag/create", json={"name": "A"}).json()["id"]
    tag_b_id = client.post("/tag/create", json={"name": "B"}).json()["id"]
    client.post(f"/entry/add-tag/{id_to}/{tag_a_id}")
    client.post(f"/entry/add-tag/{id_to}/{tag_b_id}")

    query_a = RelationQuery(relation_name="relation_a", want_source=False, category_name="Test Category",
                            required_tag="A")
    query_b = RelationQuery(relation_name="relation_b", want_source=True, category_name="Test Category",
                            required_tag="B")
    queries = [query_a, query_b]
    app.dependency_overrides.clear()

    data = get_entry_relations(session, id_from, queries)

    for entry in data.items():
        print(entry)

    assert len(queries) == 2
    assert len(data) == 1
    assert data["Test Category"][0] == id_to
    assert len(data["Test Category"]) == 1


def test_relation_query_two_categories(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    id_from = client.post("/entry/create", json=test_entry_a).json()['id']
    id_to = client.post("/entry/create", json=test_entry_b).json()['id']
    rel_type_a = client.post("/relation_type/create", json=test_relation_a).json()['id']
    rel_type_b = client.post("/relation_type/create", json=test_relation_b).json()['id']
    client.post(f"/relation/create/{rel_type_a}/{id_from}/{id_to}")
    client.post(f"/relation/create/{rel_type_b}/{id_to}/{id_from}")

    tag_a_id = client.post("/tag/create", json={"name": "A"}).json()["id"]
    tag_b_id = client.post("/tag/create", json={"name": "B"}).json()["id"]
    client.post(f"/entry/add-tag/{id_to}/{tag_a_id}")
    client.post(f"/entry/add-tag/{id_to}/{tag_b_id}")

    query_a = RelationQuery(relation_name="relation_a", want_source=False, category_name="Test Category A",
                            required_tag="A")
    query_b = RelationQuery(relation_name="relation_b", want_source=True, category_name="Test Category B",
                            required_tag="B")
    queries = [query_a, query_b]
    app.dependency_overrides.clear()

    data = get_entry_relations(session, id_from, queries)

    for entry in data.items():
        print(entry)

    assert len(queries) == 2
    assert len(data) == 2
    assert data["Test Category A"][0] == id_to
    assert len(data["Test Category A"]) == 1
    assert data["Test Category B"][0] == id_to
    assert len(data["Test Category B"]) == 1
