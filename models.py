from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from datetime import datetime, timezone


from database import Base
import schemas


class AwareDateTime(TypeDecorator):
    '''
    Stores datetimes as naive UTC and returns them tz-aware (UTC).
    SQLite drops tzinfo on read, so we normalise both directions here.
    '''
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Naive datetimes are not allowed; use a timezone-aware datetime.")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc)


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    posts: list[Post] = relationship(back_populates="author")
    comments: list[Comment] = relationship(back_populates="author")
    reactions: list[Reaction] = relationship(back_populates="author")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    post_topics: list[PostTopics] = relationship(back_populates="topic")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id: int = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    status: schemas.PostStatus = Column(String, default=schemas.PostStatus.Live) # posts are live when they are created
    like_count: int = Column(Integer, default=0) # We will increase or decrease this value in a transaction
    dislike_count:int = Column(Integer, default=0)
    created_at: datetime = Column(AwareDateTime, default=utc_now)
    expires_at: datetime = Column(AwareDateTime, nullable=False)

    author: User = relationship(back_populates="posts")
    comments: list[Comment] = relationship(back_populates="post")
    reactions: list[Reaction] = relationship(back_populates="post")
    post_topics: list[PostTopics] = relationship(back_populates="post")

    @property
    def topics(self) -> list[str]:
        '''Topic names for this post, read through the post_topics link table.'''
        return [pt.topic.name for pt in self.post_topics]

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id: int = Column(Integer, ForeignKey("users.id"))
    post_id: int = Column(Integer, ForeignKey("posts.id"))
    body = Column(String, nullable=False)
    created_at: datetime = Column(AwareDateTime, default=utc_now)

    author: User = relationship(back_populates="comments")
    post: Post = relationship(back_populates="comments")

class Reaction(Base):
    __tablename__ = "reactions"
    # Ensure a combination of author_id x post_id is unique by marking the two fields as primary keys
    author_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id: int = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    reaction = Column(String, CheckConstraint("reaction IN ('like', 'dislike')")) # prevent invalid values from being inserted into the database
    updated_at: datetime = Column(AwareDateTime, default=utc_now)

    author: User = relationship(back_populates="reactions")
    post: Post = relationship(back_populates="reactions")

class PostTopics(Base):
    __tablename__ = "post_topics"
    post_id: int = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    topic_id: int = Column(Integer, ForeignKey("topics.id"), primary_key=True)
    created_at: datetime = Column(AwareDateTime, default=utc_now)

    post: Post = relationship(back_populates="post_topics")
    topic: Topic = relationship(back_populates="post_topics")
