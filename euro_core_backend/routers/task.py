from fastapi import APIRouter

from typing import List
from fastapi import Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.task import Task, TaskBase
from euro_core_backend.dependencies import get_session


router = APIRouter(
    prefix="/task",
    tags=["Tasks"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{id}")
def get(*, session: Session = Depends(get_session), db_id: int):
    return helpers.get_by_id(session, db_id, Task)


@router.get("/get-all", response_model=List[Task])
def get_all(*, session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@router.post("/create", response_model=Task)
def create(*, session: Session = Depends(get_session), data: TaskBase):
    return helpers.create(session, data, Task)


@router.put("/update")
def update(*, session: Session = Depends(get_session), data: Task):
    return helpers.update(session, data, Task)


@router.delete("/delete/{id}")
def delete(*, session: Session = Depends(get_session), db_id: int):
    return helpers.delete(session, db_id, Task)
