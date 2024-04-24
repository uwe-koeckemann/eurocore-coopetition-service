from fastapi import APIRouter

from typing import List
from fastapi import Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.milestone_score import MilestoneScore, MilestoneScoreBase
from euro_core_backend.data.module_offer import ModuleOffer, ModuleOfferBase
from euro_core_backend.dependencies import get_session


router = APIRouter(
    prefix="/milestone-score",
    tags=["Milestone Scores"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{id}")
def get(*, session: Session = Depends(get_session), db_id: int):
    return helpers.get_by_id(session, db_id, MilestoneScore)


@router.get("/get-all", response_model=List[MilestoneScore])
def get_all(*, session: Session = Depends(get_session)):
    return session.exec(select(MilestoneScore)).all()


@router.post("/create", response_model=MilestoneScore)
def create(*, session: Session = Depends(get_session), offer: MilestoneScoreBase):
    return helpers.create(session, offer, MilestoneScore)


@router.put("/update")
def update(*, session: Session = Depends(get_session), offer: MilestoneScore):
    return helpers.update(session, offer, MilestoneScore)


@router.delete("/delete/{id}")
def delete(*, session: Session = Depends(get_session), db_id: int):
    return helpers.delete(session, db_id, MilestoneScore)
