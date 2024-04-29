from fastapi import APIRouter, HTTPException

from typing import List
from fastapi import Depends
from sqlalchemy.exc import NoResultFound
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
    try:
        team_tokens_row = session.exec(sql_query).one()
        return team_tokens_row
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"No Team-League row found.")


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
    db_row = session.exec(
        select(TeamTokens)
        .where(TeamTokens.team_id == team.team_id)
        .where(TeamTokens.league_id == team.league_id)).one()
    if not db_row:
        raise HTTPException(status_code=404, detail=f"Team-League row not found. Could not update {row}")
    row_data = team.dict(exclude_unset=True)
    for key, value in row_data.items():
        setattr(db_row, key, value)
    session.add(db_row)
    session.commit()
    session.refresh(db_row)
    return db_row


@router.delete("/delete/{team_id}/{league_id}")
def delete_team(*, session: Session = Depends(get_session),
                team_id: int,
                league_id: int):
    db_row = session.exec(
        select(TeamTokens)
        .where(TeamTokens.team_id == team_id)
        .where(TeamTokens.league_id == league_id)).one()
    session.delete(db_row)
    session.commit()
    return db_row
