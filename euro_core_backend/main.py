import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel

from euro_core_backend.routers import (tag, entry, relation_type, relation, team_tokens, module_offer, module_usage,
                                       milestone, milestone_score, team, robot)
from euro_core_backend.dependencies import get_session, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    pass


app = FastAPI(
    dependencies=[Depends(get_session)],
    lifespan=lifespan

)
app.include_router(tag.router)
app.include_router(entry.router)
app.include_router(relation_type.router)
app.include_router(relation.router)
app.include_router(team_tokens.router)
app.include_router(module_offer.router)
app.include_router(module_usage.router)
app.include_router(milestone.router)
app.include_router(milestone_score.router)
app.include_router(team.router)
app.include_router(robot.router)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

