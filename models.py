from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey,JSON, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


from database import Base
import schemas


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    posts: list[Post] = relationship(back_populates="author")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id: int = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    status: schemas.PostStatus = Column(String, default=schemas.PostStatus.Live) # posts are live when they are created
    like_count: int = Column(Integer, default=0) # We will increase or decrease this value in a transaction
    dislike_count:int = Column(Integer, default=0)
    created_at: int = Column(BigInteger, default=lambda: datetime.now(timezone.utc).timestamp())
    expires_at: int = Column(BigInteger, nullable=False)

    author: User = relationship(back_populates="posts")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id: int = Column(Integer, ForeignKey("users.id"))
    post_id: int = Column(Integer, ForeignKey("posts.id"))
    body = Column(String, nullable=False)
    created_at: int = Column(BigInteger, default=lambda: datetime.now(timezone.utc).timestamp())

class Reaction(Base):
    __tablename__ = "reactions"
    # Ensure a combination of author_id x post_id is unique by marking the two fields as primary keys
    author_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id: int = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    reaction = Column(String, CheckConstraint("reaction IN ('like', 'dislike')")) # prevent invalid values from being inserted into the database
    updated_at: int = Column(BigInteger, default=lambda: datetime.now(timezone.utc).timestamp())


class PostTopics(Base):
    __tablename__ = "post_topics"
    post_id: int = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    topic_id: int = Column(Integer, ForeignKey("topics.id"), primary_key=True)
    created_at: int = Column(BigInteger, default=lambda: datetime.now(timezone.utc).timestamp())
    