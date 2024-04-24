from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from euro_core_backend.data.entry import Entry
from euro_core_backend.data.relation import Relation
from euro_core_backend.data.relation_type import RelationType
from euro_core_backend.data.tag import Tag
from euro_core_backend.relation_query import RelationQuery


_tag_id_cache = {}
_relation_id_cache = {}


def get_by_id(session, db_id, data_type):
    data = session.get(data_type, db_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"No {data_type.__name__} row found with ID: {db_id}")
    return data


def get_by_name(session, name, data_type):
    try:
        tag = session.exec(select(data_type).where(data_type.name == name)).one()
        return tag
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"No {data_type.__name__} row found with name: {name}")


def _lazy_get_tag_id(session, name):
    if name in _tag_id_cache.keys():
        return _tag_id_cache[name]
    tag_id = get_by_name(session, name, Tag).id
    _tag_id_cache[name] = tag_id
    return tag_id


def _lazy_get_relation_id(session, name):
    if name in _relation_id_cache.keys():
        return _relation_id_cache[name]
    relation_id = get_by_name(session, name, RelationType).id
    _relation_id_cache[name] = relation_id
    return relation_id


def get_entry_relations(session, db_id, relations: List[RelationQuery]):
    """
    Given an entry id and a list of relation queries, collect all related
    objects in a dictionary and return it.

    :param session:
    :param db_id:
    :param relations:
    :return:
    """
    data = {}
    for query in relations:
        get_entry_relations_single(session, db_id, query, data)
    return data


def get_entry_relations_single(session, db_id, query: RelationQuery, data):
    """
    Look up related entries based on a relation query.

    :param session:
    :param db_id:
    :param query: Query to execute
    :param data: Dictionary to store related objects
    """
    relation_id = _lazy_get_relation_id(session, query.relation_name)
    tag_id = _lazy_get_tag_id(session, query.required_tag)
    if query.category_name not in data.keys():
        data[query.category_name] = []
    if query.want_source:
        sql_query = select(Relation).where(Relation.to_id == db_id).where(Relation.relation_type_id == relation_id)
        relations = session.exec(sql_query).all()
    else:
        sql_query = select(Relation).where(Relation.from_id == db_id, Relation.relation_type_id == relation_id)
        relations = session.exec(sql_query).all()

    for relation in relations:
        if query.want_source:
            entry = get_by_id(session, relation.from_id, Entry)
        else:
            entry = get_by_id(session, relation.to_id, Entry)
        for tag in entry.tags:
            if tag.id == tag_id:
                if entry.id not in data[query.category_name]:
                    data[query.category_name].append(entry.id)
                break


def create(session, data, data_type):
    db_data = data_type.model_validate(data)
    session.add(db_data)
    session.commit()
    return db_data


def update(session, row, db_type):
    db_row = session.get(db_type, row.id)
    if not db_row:
        raise HTTPException(status_code=404, detail=f"{db_type.__name__} not found. Could not update {row}")
    row_data = row.dict(exclude_unset=True)
    for key, value in row_data.items():
        setattr(db_row, key, value)
    session.add(db_row)
    session.commit()
    session.refresh(db_row)
    return db_row


def delete(session, row_id, db_type):
    db_row = session.get(db_type, row_id)
    if not db_row:
        raise HTTPException(status_code=404, detail=f"Cannot delete {db_row} from {db_type.__name__}: not found")
    # TODO: Add constraints that may forbid delete of linked data or perform additional deletes
    session.delete(db_row)
    session.commit()
    return db_row


def assert_exists(session, row_id, db_type):
    db_row = session.get(db_type, row_id)
    if not db_row:
        raise HTTPException(status_code=404, detail=f"Could not find {db_type.__name__} with id: {row_id}")