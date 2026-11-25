from pydantic import BaseModel, ConfigDict, EmailStr, Field, AwareDatetime
from datetime import datetime, timezone
from enum import StrEnum


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

class PostStatus(StrEnum):
    Expired = "Expired"
    Live = "Live"
class Reaction(StrEnum):
    Dislike = "dislike"
    Like = "like"

class CommentResponse(BaseModel):
    id: int
    author: UserResponse
    post_id: int
    body: str = Field(min_length=3)
    created_at: AwareDatetime

class PostResponse(BaseModel):
    id: int
    author: UserResponse
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)
    topics: set[str]  = Field(min_length=1) # Topic names will be filled in as strings
    created_at: AwareDatetime
    expires_at: AwareDatetime
    status: PostStatus
    like_count: int = Field(min=0)
    dislike_count: int = Field(min=0)
    comments: list[CommentResponse]

class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)
    topics: list[str]  = Field(min_length=1)
    expires_at: AwareDatetime = Field(gt=datetime.now(timezone.utc)) # Expiration time must be in the future

class ReactionCreate(BaseModel):
    value: Reaction

class ReactionResponse(BaseModel):
    post_id: int
    likes: int
    dislikes: int
    updated_at: AwareDatetime

class CommentCreate(BaseModel):
    body: str = Field(min_length=3)