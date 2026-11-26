from fastapi import FastAPI
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

import models
from database import engine, SessionLocal
from routers import auth, posts, topics
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
    app.include_router(posts.router, prefix="/posts")
    app.include_router(topics.router, prefix="/topics")

    @app.get("/")
    @app.get("/health")
    def home():
        return {"message": "Piazza API Healthy"}

    return app