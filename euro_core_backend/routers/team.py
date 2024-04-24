from fastapi import APIRouter

from typing import List
from fastapi import HTTPException, Depends
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.entry import Entry, EntryBase
from euro_core_backend.data.entry_tag_link import EntryTagLink
from euro_core_backend.data.relation import Relation
from euro_core_backend.data.relation_type import RelationType
from euro_core_backend.data.tag import Tag
from euro_core_backend.data.team_tokens import TeamTokens
from euro_core_backend.dependencies import get_session
from euro_core_backend.relation_query import RelationQuery

router = APIRouter(
    prefix="/team",
    tags=["Teams"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{team_id}/{league_id}")
def get_by_id(*,
              session: Session = Depends(get_session),
              team_id: int,
              league_id: int):
    team_entry = helpers.get_by_id(session, team_id, Entry)
    if not team_entry:
        raise HTTPException(status_code=404)
    league_entry = helpers.get_by_id(session, team_id, Entry)
    if not league_entry:
        raise HTTPException(status_code=404)
    team_id = team_entry.id

    sql_query = (select(TeamTokens)
                 .where(TeamTokens.team_id == team_id)
                 .where(TeamTokens.league_id == league_entry.id))
    team_tokens_row = session.exec(sql_query).one()

    # team_tokens = helpers.get()

    queries = [
        RelationQuery("uses", "Robot", False, "Robots"),
    ]

    data = helpers.get_entry_relations(session, team_id, queries)

    team_entry.league = league_entry.name
    team_entry.robots = data["Robots"]
    team_entry.points = team_tokens_row.points

    return team_entry


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
