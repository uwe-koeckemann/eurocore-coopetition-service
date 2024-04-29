from typing import Optional

from sqlmodel import Field, SQLModel


class MilestoneBase(SQLModel):
    league_id: int = Field(default=None, foreign_key="entry.id")
    task_id: int = Field(default=None, foreign_key="task.id")
    milestone_seq_nr: int = Field(default=None)
    name: str = Field(default=None, max_length=80)
    points: int = Field(default=0)  # b_mn


class Milestone(MilestoneBase, table=True):
    __tablename__ = "milestone"
    id: Optional[int] = Field(default=None, primary_key=True)
