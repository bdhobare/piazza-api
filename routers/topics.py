from database import get_db
import schemas
import models
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from security import get_current_user

router = APIRouter()


@router.get("/{topic}/most-active", response_model=list[schemas.PostResponse], status_code=200)
def get_most_active_post(topic: str, _: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if the topic exists
    topic_obj = db.scalar(
        select(models.Topic).where(models.Topic.name == topic)
    )
    if topic_obj is None:
        raise HTTPException(status_code=422, detail=f"Topic '{topic}' not found")
    
    now_utc = datetime.now(timezone.utc)
    post = db.scalars(
        select(models.Post)
        .join(models.PostTopics)
        .join(models.Topic)
        .where(models.Topic.name == topic)
        .where(now_utc < models.Post.expires_at)  # Only consider live posts
        .order_by(
            (models.Post.like_count + models.Post.dislike_count).desc(),
            models.Post.created_at.desc(),
            models.Post.id.asc()
        )
    ).first()

    if post is None:
        return []
    # Get comments for the post
    comments = db.scalars(
        select(models.Comment)
        .where(models.Comment.post_id == post.id)
        .order_by(models.Comment.created_at.asc())
    ).all()
    
    postresponse = schemas.PostResponse(
            id=post.id,
            author=schemas.UserResponse(
                id=post.author.id,
                name=post.author.name,
                email=post.author.email
            ),
            title=post.title,
            body=post.body,
            topics=post.topics,
            created_at=post.created_at,
            expires_at=post.expires_at,
            status=post.status,
            like_count=post.like_count,
            dislike_count=post.dislike_count,
            comments=[schemas.CommentResponse(
                id=comment.id,
                author=schemas.UserResponse(
                    id=comment.author.id,
                    name=comment.author.name,
                    email=comment.author.email
                ),
                post_id=comment.post_id,
                body=comment.body,
                created_at=comment.created_at
            ) for comment in comments]
        )
    return [postresponse]            
    
    