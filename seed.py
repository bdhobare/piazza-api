from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

import models

'''
This file is used to seed the database during application startup. 
For now we only seed the post categories.
'''
DEFAULT_TOPICS = [
    "Politics",
    "Health",
    "Sport",
    "Tech"
] # TODO: Can we feed this through the config file?

def seed_topics(db: Session = Depends(get_db)):
    '''
    We fetch existing topics in the DB and insert missing ones
    '''
    existing_names = set(Session.scalars(select(models.Topic.name)).all())
    new_topics = [
        models.Topic(name=name) for name in DEFAULT_TOPICS if name not in existing_names
    ]
    Session.add_all(new_topics)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise # raise the same exception to terminate startup