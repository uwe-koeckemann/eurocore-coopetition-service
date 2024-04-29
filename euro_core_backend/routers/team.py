from fastapi import APIRouter

from typing import List
from fastapi import HTTPException, Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.entry import Entry
from euro_core_backend.data.team import Team
from euro_core_backend.data.team_tokens import TeamTokens
from euro_core_backend.dependencies import get_session
from euro_core_backend.relation_query import RelationQuery
from euro_core_backend.routers import relation, team_tokens, entry

router = APIRouter(
    prefix="/team",
    tags=["Teams"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


def _fetch_additional_team_info(session: Session, team_entry: Entry, league_entry: Entry) -> Team:
    team_tokens_row = team_tokens.get_team(session, team_entry.id, league_entry.id)

    queries = [
        RelationQuery("uses", "Robot", False, "Robots"),
        RelationQuery("member_of", "Group", False, "Groups")
    ]

    data = helpers.get_entry_relations(session, team_entry.id, queries)

    team = Team(
        id=team_entry.id,
        name=team_entry.name,
        league_id=league_entry.id,
        league_name=league_entry.name,
        robots=data["Robots"],
        groups=data["Groups"],
        points=team_tokens_row.points,
    )

    return team


def _add_team_relations(session, team):
    # Add relations to robots and groups
    member_of_id = helpers.lazy_get_relation_id(session, "member_of")
    for group_id in team.group_ids:
        relation.create_relation(session, member_of_id, team.id, group_id)
    uses_id = helpers.lazy_get_relation_id(session, "uses")
    for robot_id in team.robot_ids:
        relation.create_relation(session, uses_id, team.id, robot_id)


@router.get("/get/{team_id}/{league_id}",
            response_model=Team,
            description="Get a team's data for a specific league.")
def get_by_id(*,
              session: Session = Depends(get_session),
              team_id: int,
              league_id: int):
    team_entry = helpers.get_by_id(session, team_id, Entry)
    if not team_entry:
        raise HTTPException(status_code=404)
    league_entry = helpers.get_by_id(session, league_id, Entry)
    if not league_entry:
        raise HTTPException(status_code=404)

    return _fetch_additional_team_info(session, team_entry, league_entry)


@router.get("/get-by-name/{team_name}/{league_name}", response_model=Team)
def get_entry_by_name(*,
                      session: Session = Depends(get_session),
                      team_name: str,
                      league_name: str):
    team_entry = helpers.get_by_name(session, team_name, Entry)
    if not team_entry:
        raise HTTPException(status_code=404)
    league_entry = helpers.get_by_name(session, league_name, Entry)
    if not league_entry:
        raise HTTPException(status_code=404)

    return _fetch_additional_team_info(session, team_entry, league_entry)


@router.get("/get-all", response_model=List[Team])
def get_all_entries(*,
                    session: Session = Depends(get_session)):
    results = []
    for token_row in session.exec(select(TeamTokens)):
        results.append(get_by_id(session, token_row.id, token_row.league_id))
    return results


@router.post("/create", response_model=Team)
def create(*,
           session: Session = Depends(get_session),
           team: Team):
    league_entry = helpers.get_by_id(session, team.league_id, Entry)
    if not league_entry:
        raise HTTPException(status_code=404, detail="League not found.")

    # Create team entry
    team_entry = helpers.create(session, team, Entry)

    # Add relations to robots and groups
    _add_team_relations(session, team)

    # Create team_tokens row
    team_tokens_row = TeamTokens(
        team_id=team_entry.id,
        league_id=league_entry.id,
        points=team.points,
    )
    team_tokens.create_team(session, team_tokens_row)

    # Add id to team argument and return
    team.id = team_entry.id
    team.league_name = league_entry.name

    return team


@router.put("/update", response_model=Team)
def update_entry(*,
                 session: Session = Depends(get_session),
                 team: Team):
    helpers.update(session, team, Entry)
    # Create team_tokens row
    team_tokens_row = TeamTokens(
        team_id=team.id,
        league_id=team.league_id,
        points=team.points,
    )
    team_tokens.update_team(session, team_tokens_row)

    # Add all relations
    # relation.delete_relations_of_entry(session, team.id)
    _add_team_relations(session, team)

    return team


@router.delete("/delete/{team_id}/{league_id}", response_model=Team)
def delete_team(*,
                session: Session = Depends(get_session),
                team_id: int,
                league_id: int):
    team = get_by_id(session, team_id, league_id)
    relation.delete_relations_of_entry(session, team_id)
    team_tokens_row = team_tokens.get_team(session, team_id, league_id)
    session.delete(team_tokens_row)
    helpers.delete(session, team_id, Entry)
    return team
