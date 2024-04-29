from fastapi import APIRouter

from typing import List
from fastapi import Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.relation_type import RelationType
from euro_core_backend.dependencies import get_session

router = APIRouter(
    prefix="/relation-type",
    tags=["Relation Type"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{relation_type_id}", response_model=RelationType)
def get_relation_type(*, session: Session = Depends(get_session),
                      relation_type_id: int):
    return helpers.get_by_id(session, relation_type_id, RelationType)


@router.get("/get-by-name/{name}", response_model=RelationType)
def get_relation_type_by_name(*, session: Session = Depends(get_session),
                              name: str):
    return helpers.get_by_name(session, name, RelationType)


@router.get("/get-all", response_model=List[RelationType])
def get_all_relation_types(*, session: Session = Depends(get_session)):
    results = session.exec(select(RelationType))
    return results.all()


@router.post("/create", response_model=RelationType)
def create_relation_type(*,
                         session: Session = Depends(get_session),
                         relation_type: RelationType):
    return helpers.create(session, relation_type, RelationType)


@router.put("/update/", response_model=RelationType)
def update_relation_type(*,
                         session: Session = Depends(get_session),
                         relation_type: RelationType):
    return helpers.update(session, relation_type, RelationType)


@router.delete("/delete/{relation_type_id}", response_model=RelationType)
def delete_relation_type(*, session: Session = Depends(get_session),
                         relation_type_id: int):
    return helpers.delete(session, relation_type_id, RelationType)
