from typing import Optional, List
from sqlmodel import Field

from euro_core_backend.data.entry import EntryBase


class Robot(EntryBase):
    user_ids: List[int]
    hardware_ids: List[int]
    module_ids: List[int]



