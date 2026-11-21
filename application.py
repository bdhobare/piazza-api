from fastapi import FastAPI
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

import models
from database import engine, SessionLocal
import database
from routers import auth, profile
from seed import seed_topics


@asynccontextmanager
async def lifespan(app: FastAPI):
  '''
  Seeds the database with the topics during application startup
  '''
  models.Base.metadata.create_all(bind=engine)
  with SessionLocal() as db:
    seed_topics(db)
  yield
  engine.dispose()


app = FastAPI(lifespan=lifespan)

def create_app(db_engine=engine):
    models.Base.metadata.create_all(bind=db_engine)
    app = FastAPI(lifespan=lifespan)
    app.include_router(auth.router, prefix="/auth")
    app.include_router(profile.router, prefix="/profile")

    @app.get("/")
    @app.get("/health")
    def home():
        return {"message": "Piazza API healthy"}

    return app