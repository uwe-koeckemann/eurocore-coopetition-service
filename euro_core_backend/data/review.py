from typing import Optional
from sqlmodel import Field, SQLModel


class ReviewBase(SQLModel):
    entry_id: int = Field(default=None, foreign_key="entry.id")
    author_id: int = Field(default=None, foreign_key="entry_id")
    review: Optional[str] = Field(max_length=500)


class Review(ReviewBase, table=True):
    __tablename__ = "review"
    id: Optional[int] = Field(default=None, primary_key=True)


class EntryUpdate(SQLModel):
    entry_id: Optional[int] = None
    author_id: Optional[int] = None
    review: Optional[str] = None
