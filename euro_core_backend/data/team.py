from typing import Optional, List
from sqlmodel import Field

from euro_core_backend.data.entry import EntryBase


class Team(EntryBase):
    id: Optional[int] = Field(default=None)
    robot_ids: List[int] = Field(default=[])
    group_ids: List[int] = Field(default=[])



