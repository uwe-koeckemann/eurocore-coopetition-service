from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class MilestoneScoreBase(SQLModel):
    team: int = Field(foreign_key="entry.id")
    milestone_id: int = Field(foreign_key="milestone.id")
    success: bool = Field(default=False)
    transfer: bool = Field(default=False)
    condition_level: float = Field(default=1.0)
    subjective_score: float = Field(default=0.0)
    penalty: float = Field(default=0.0)


class MilestoneScore(MilestoneScoreBase, table=True):
    __tablename__ = "milestone_score"
    id: Optional[int] = Field(default=None, primary_key=True)


class MilestoneScoreUpdate(SQLModel):
    team: Optional[int] = None
    milestone_id: Optional[int] = None
    success: Optional[bool] = None
    transfer: Optional[bool] = None
    condition_level: Optional[float] = None
    subjective_score: Optional[float] = None
    penalty: Optional[float] = None
