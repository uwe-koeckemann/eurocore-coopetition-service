from dataclasses import dataclass


@dataclass
class RelationQuery:
    relation_name: str
    required_tag: str
    want_source: bool
    category_name: str

