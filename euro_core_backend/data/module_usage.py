from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class ModuleUsageBase(SQLModel):
    consumer_team_id: int = Field(foreign_key="entry.id")
    module_offer_id: int = Field(foreign_key="module_offer.id")
    milestone_id: int = Field(foreign_key="milestone.id")


class ModuleUsage(ModuleUsageBase, table=True):
    __tablename__ = "module_usage"
    id: Optional[int] = Field(default=None, primary_key=True)


class ModuleUsageUpdate(SQLModel):
    consumer_team_id: Optional[int] = None
    module_offer_id: Optional[int] = None

