from sqlmodel import Field, SQLModel


class TeamTokens(SQLModel, table=True):
    """
    Represents a team participating in a league.
    """
    __tablename__ = "team_tokens"
    team_id: int = Field(default=None, foreign_key="entry.id", primary_key=True)
    league_id: int = Field(default=None, foreign_key="entry.id", primary_key=True)
    points: int = Field(default=0)
