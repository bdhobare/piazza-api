from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from enum import IntEnum, StrEnum


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TopicResponse(BaseModel): # Topics will be prepopulated in the database
    id: int
    name: str

class PostStatus(IntEnum):
    Expired = 0
    Live = 1

class Reaction(StrEnum):
    Dislike = "dislike"
    Like = "like"

class UserSimple(BaseModel):
  '''
  Stripped down details of a user to be appended in Posts and Comments responses
  '''
  id: int
  name: str

class CommentResponse(BaseModel):
    id: int
    author: UserSimple
    post_id: int
    content: str = Field(min_length=3)
    created_at: datetime # Unix timestamp

class PostResponse(BaseModel):
    id: int
    author: UserSimple
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)
    topics: set[str]  = Field(min_length=1) # Topic names will be filled in as strings
    created_at: datetime # Unix timestamp, so that the caller can display it in the local timestamp
    expires_at: datetime
    status: PostStatus
    like_count: int = Field(min=0)
    dislike_count: int = Field(min=0)
    comments: list[CommentResponse]


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)
    topics: list[str]  = Field(min_length=1)
    expires_at: datetime

class ReactionCreate(BaseModel):
    value: Reaction

class ReactionResponse(BaseModel):
    post_id: int
    likes: int
    dislikes: int
    updated_at: datetime
