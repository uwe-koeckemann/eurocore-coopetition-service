from fastapi import APIRouter

from typing import List
from fastapi import HTTPException, Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.entry import Entry, EntryBase
from euro_core_backend.data.entry_tag_link import EntryTagLink
from euro_core_backend.data.robot import Robot
from euro_core_backend.data.tag import Tag
from euro_core_backend.dependencies import get_session
from euro_core_backend.relation_query import RelationQuery
from euro_core_backend.routers import relation, entry

router = APIRouter(
    prefix="/robot",
    tags=["Robots"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


def _fetch_additional_robot_info(session: Session, robot_entry: Entry) -> Robot:
    queries = [
        RelationQuery("uses", "Team", True, "Users"),
        RelationQuery("part_of", "Hardware", False, "Hardware"),
        RelationQuery("supports", "Module", False, "Modules")
    ]

    data = helpers.get_entry_relations(session, robot_entry.id, queries)

    robot = Robot(
        id=robot_entry.id,
        name=robot_entry.name,
        description=robot_entry.description,
        tags=robot_entry.tags,
        user_ids=data["Users"],
        hardware_ids=data["Hardware"],
        module_ids=data["Modules"],
    )

    return robot


def _add_robot_relations(session, robot):
    uses_id = helpers.lazy_get_relation_id(session, "uses")
    for user_id in robot.user_ids:
        relation.create_relation(session=session,
                                 relation_type_id=uses_id,
                                 from_id=user_id,
                                 to_id=robot.id)

    member_of_id = helpers.lazy_get_relation_id(session, "part_of")
    for hardware_id in robot.hardware_ids:
        relation.create_relation(session=session,
                                 relation_type_id=member_of_id,
                                 from_id=hardware_id,
                                 to_id=robot.id)

    module_of_id = helpers.lazy_get_relation_id(session, "supports")
    for module_id in robot.module_ids:
        relation.create_relation(session=session,
                                 relation_type_id=module_of_id,
                                 from_id=robot.id,
                                 to_id=module_id)


@router.get("/get/{robot_id}", response_model=Robot)
def get_by_id(*,
              session: Session = Depends(get_session),
              robot_id: int):
    robot_entry = helpers.get_by_id(session, robot_id, Entry)
    if not robot_entry:
        raise HTTPException(status_code=404)
    return _fetch_additional_robot_info(session, robot_entry)


@router.get("/get-by-name/{name}", response_model=Entry)
def get_by_name(*,
                session: Session = Depends(get_session),
                name: str):
    robot_entry = helpers.get_by_name(session, name, Entry)
    if not robot_entry:
        raise HTTPException(status_code=404)
    return _fetch_additional_robot_info(session, robot_entry)


@router.get("/get-all", response_model=List[Robot])
def get_all(*,
            session: Session = Depends(get_session)):
    robot_entries = entry.get_all_with_tag(session, helpers.lazy_get_tag_id(session, "Robot"))
    results = []
    for robot_entry in robot_entries:
        results.append(_fetch_additional_robot_info(session, robot_entry))
    return results


@router.post("/create", response_model=Robot)
def create(*,
           session: Session = Depends(get_session),
           robot: Robot):
    robot_entry = helpers.create(session, robot, Entry)
    robot.id = robot_entry.id
    _add_robot_relations(session, robot)
    return robot


@router.put("/update", response_model=Robot)
def update(*,
           session: Session = Depends(get_session),
           robot: Robot):
    # relation.delete_relations_of_entry(session, robot.id)
    _add_robot_relations(session, robot)

    return robot


@router.delete("/delete/{robot_id}", response_model=Robot)
def delete(*,
           session: Session = Depends(get_session),
           robot_id: int):
    robot = get_by_id(session, robot_id)
    relation.delete_relations_of_entry(session, robot_id)
    helpers.delete(session, robot_id, Entry)
    return robot
