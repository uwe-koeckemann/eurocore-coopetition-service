from fastapi import APIRouter

from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from euro_core_backend import helpers
from euro_core_backend.data.entry import Entry, EntryBase
from euro_core_backend.data.entry_tag_link import EntryTagLink
from euro_core_backend.data.tag import Tag
from euro_core_backend.dependencies import get_session

router = APIRouter(
    prefix="/entry",
    tags=["Entries"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "End-point does not exist"}},
)


@router.get("/get/{entry_id}", response_model=Entry)
def get_entry(*,
              session: Session = Depends(get_session),
              entry_id: int):
    return helpers.get_by_id(session, entry_id, Entry)


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


@router.post("/get-all-with-tag/{tag_id}", response_model=List[Entry])
def get_all_with_tag(*,
                     session: Session = Depends(get_session),
                     tag_id: int):
    all_entries = session.exec(select(Entry))
    selected = []
    for entry in all_entries:
        for entry_tag_id in entry.tags:
            if entry_tag_id == tag_id:
                selected.append(entry)
                break
    return selected


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
