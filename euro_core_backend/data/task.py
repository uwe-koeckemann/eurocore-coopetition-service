from typing import Optional

from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    league_id: int = Field(default=None, foreign_key="entry.id")
    task_seq_nr: int = Field(default=None)
    name: str = Field(max_length=100, unique=True)


class Task(TaskBase, table=True):
    __tablename__ = "task"
    id: Optional[int] = Field(default=None, primary_key=True)

