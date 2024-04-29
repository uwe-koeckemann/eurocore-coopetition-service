from fastapi import APIRouter, HTTPException

from typing import List
from fastapi import Depends
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.entry import Entry
from euro_core_backend.data.relation import Relation
from euro_core_backend.data.relation_type import RelationType
from euro_core_backend.dependencies import get_session

router = APIRouter(
    prefix="/relation",
    tags=["Relations"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get-by-type/{relation_type_id}", response_model=List[Relation])
def get_by_type(*, session: Session = Depends(get_session),
                relation_type_id: int) -> List[Relation]:
    return session.exec(select(Relation).where(Relation.relation_type_id == relation_type_id)).all()


@router.get("/get-outgoing/{source_entry_id}", response_model=List[Relation])
def get_outgoing(*, session: Session = Depends(get_session),
                 source_entry_id: int) -> List[Relation]:
    return session.exec(select(Relation).where(Relation.from_id == source_entry_id)).all()


@router.get("/get-incoming/{target_entry_id}", response_model=List[Relation])
def get_incoming(*, session: Session = Depends(get_session),
                 target_entry_id: int) -> List[Relation]:
    return session.exec(select(Relation).where(Relation.to_id == target_entry_id)).all()


@router.post("/create/{relation_type_id}/{from_id}/{to_id}", response_model=Relation)
def create_relation(*, session: Session = Depends(get_session),
                    relation_type_id: int,
                    from_id: int,
                    to_id: int):
    helpers.assert_exists(session, relation_type_id, RelationType)
    helpers.assert_exists(session, from_id, Entry)
    helpers.assert_exists(session, to_id, Entry)
    return helpers.create(session, Relation(relation_type_id=relation_type_id, from_id=from_id, to_id=to_id), Relation)


@router.delete("/delete/{relation_type_id}/{from_id}/{to_id}", response_model=Relation)
def delete_relation(*, session: Session = Depends(get_session),
                    relation_type_id: int,
                    from_id: int,
                    to_id: int):
    try:
        db_row = session.exec(select(Relation)
                              .where(Relation.relation_type_id == relation_type_id)
                              .where(Relation.from_id == from_id)
                              .where(Relation.to_id == to_id)).one()
        session.delete(db_row)
        session.commit()
        return db_row
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Relation {relation_type_id}/{from_id}/{to_id} does not exist")


@router.delete("/delete-relations/{entry_id}", response_model=List[Relation])
def delete_relations_of_entry(*, session: Session = Depends(get_session),
                              entry_id: int):
    to_delete = list(session.exec(select(Relation).where(Relation.to_id == entry_id)))
    to_delete.extend(session.exec(select(Relation).where(Relation.from_id == entry_id)))

    for row in to_delete:
        session.delete(row)
    session.commit()

    return to_delete
