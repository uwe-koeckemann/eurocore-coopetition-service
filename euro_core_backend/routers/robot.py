from fastapi import APIRouter

from typing import List
from fastapi import HTTPException, Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.entry import Entry, EntryBase
from euro_core_backend.data.entry_tag_link import EntryTagLink
from euro_core_backend.data.relation import Relation
from euro_core_backend.data.relation_type import RelationType
from euro_core_backend.data.robot import Robot
from euro_core_backend.data.tag import Tag
from euro_core_backend.data.team_tokens import TeamTokens
from euro_core_backend.dependencies import get_session
from euro_core_backend.relation_query import RelationQuery

router = APIRouter(
    prefix="/robot",
    tags=["Robots"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{robot_id}", response_model=Robot)
def get_by_id(*,
              session: Session = Depends(get_session),
              robot_id: int):
    robot_entry = helpers.get_by_id(session, robot_id, Entry)
    if not robot_entry:
        raise HTTPException(status_code=404)

    queries = [
        RelationQuery("uses", "Team", True, "Teams"),
        RelationQuery("part_of", "Hardware", False, "Hardware"),
        RelationQuery("supports", "Module", False, "Modules")
    ]

    data = helpers.get_entry_relations(session, robot_id, queries)

    robot = Robot(
        id=robot_entry.id,
        name=robot_entry.name,
        description=robot_entry.description,
        user_ids=data["Teams"],
        hardware_ids=data["Hardware"],
        module_ids=data["Modules"]
    )

    return robot


@router.get("/get-by-name/{name}", response_model=Entry)
def get_entry_by_name(*,
                      session: Session = Depends(get_session),
                      name: str):
    return helpers.get_by_name(session, name, Entry)


@router.get("/get-all", response_model=List[Entry])
def get_all_entries(*,
                    session: Session = Depends(get_session), ):
    results = session.exec(select(Entry))
    return results.all()


@router.post("/create", response_model=Entry)
def create_entry(*,
                 session: Session = Depends(get_session),
                 entry: EntryBase):
    return helpers.create(session, entry, Entry)


@router.post("/add-tag/{entry_id}/{tag_id}")
def add_entry_tag(*,
                  session: Session = Depends(get_session),
                  entry_id: int,
                  tag_id: int):
    new_entry_entry_link = EntryTagLink(entry_id=entry_id, tag_id=tag_id)
    session.add(new_entry_entry_link)
    session.commit()
    return {}


@router.get("/get-tags/{entry_id}", response_model=List[Tag])
def get_all_tags(*,
                 session: Session = Depends(get_session),
                 entry_id: int):
    db_entry = session.get(Entry, entry_id)

    if not db_entry:
        raise HTTPException(status_code=404, detail=f"Entry not found (ID): {entry_id}")
    return db_entry.tags


@router.put("/update", response_model=Entry)
def update_entry(*,
                 session: Session = Depends(get_session),
                 entry: Entry):
    return helpers.update(session, entry, Entry)


@router.delete("/delete/{entry_id}", response_model=Entry)
def delete_entry(*,
                 session: Session = Depends(get_session),
                 entry_id: int):
    return helpers.delete(session, entry_id, Entry)
