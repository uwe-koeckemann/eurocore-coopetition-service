from fastapi import APIRouter

from typing import List
from fastapi import Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.milestone import Milestone, MilestoneBase
from euro_core_backend.dependencies import get_session


router = APIRouter(
    prefix="/milestone",
    tags=["Milestones"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{id}")
def get(*, session: Session = Depends(get_session), db_id: int):
    return helpers.get_by_id(session, db_id, Milestone)


@router.get("/get-all", response_model=List[Milestone])
def get_all(*, session: Session = Depends(get_session)):
    return session.exec(select(Milestone)).all()


@router.post("/create", response_model=Milestone)
def create(*, session: Session = Depends(get_session), data: MilestoneBase):
    return helpers.create(session, data, Milestone)


@router.put("/update")
def update(*, session: Session = Depends(get_session), data: Milestone):
    return helpers.update(session, data, Milestone)


@router.delete("/delete/{id}")
def delete(*, session: Session = Depends(get_session), db_id: int):
    return helpers.delete(session, db_id, Milestone)
