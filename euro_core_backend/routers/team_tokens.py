from fastapi import APIRouter

from typing import List
from fastapi import Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.dependencies import get_session
from euro_core_backend.data.team_tokens import TeamTokens

router = APIRouter(
    prefix="/team-tokens",
    tags=["Team Tokens"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{team_id}/{league_id}", response_model=TeamTokens)
def get_team(*, session: Session = Depends(get_session),
             team_id: int,
             league_id: int) -> TeamTokens:
    sql_query = (select(TeamTokens)
                 .where(TeamTokens.team_id == team_id)
                 .where(TeamTokens.league_id == league_id))
    team_tokens_row = session.exec(sql_query).one()
    return team_tokens_row


@router.get("/get-all", response_model=List[TeamTokens])
def get_all_teams(*, session: Session = Depends(get_session)):
    return session.exec(select(TeamTokens)).all()


@router.post("/create", response_model=TeamTokens)
def create_team(*, session: Session = Depends(get_session),
                team: TeamTokens):
    return helpers.create(session, team, TeamTokens)


@router.put("/update")
def update_team(*, session: Session = Depends(get_session),
                team: TeamTokens):
    return helpers.update(session, team, TeamTokens)


@router.delete("/delete/{team_id}")
def delete_team(*, session: Session = Depends(get_session),
                team_id: int):
    return helpers.delete(session, team_id, TeamTokens)
