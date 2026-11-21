from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select

import models
import schemas
from security import get_current_user
from database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.PostResponse, status_code=201)
def create_post(request: models.PostCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    We use a transaction here to ensure inserts into posts and post_topics succeed or fail.
    '''
    # Remove duplicated topic names
    request_topics = set(request.topics)
    with db.begin():
        topics = db.scalars(
            select(models.Topic).where(models.Topic.name.in_(request_topics))
        ).all()
        # Check that all topic names sent exist in the server
        if len(topics) != len(request_topics):
            found_names = {t.name for t in topics}
            missing = request_topics - found_names
            raise HTTPException(
                status_code=400,
                detail=f"Invalid topics: {sorted(missing)}",
        )
        post = models.Post(
            author_id = current_user.id,
            title = request.title,
            body = request.body,
            status = schemas.PostStatus.Live,
            like_count = 0,
            dislike_count = 0,
            expires_at = request.expires_at
        )
        db.add(post)
        db.flush() # Retrieves the post.id for use in post_topics
        
        post_topics = [
            models.PostTopics(post_id=post.id, topic_id=topic_id)
            for topic_id in topics
        ]
        db.add_all(post_topics)
        return schemas.PostResponse(
            id=post.id,
            author = schemas.UserSimple(
                id = current_user.id,
                name = current_user.name
            ),
            title=post.title,
            body = post.body,
            topics=request_topics,
            created_at=post.created_at,
            expires_at=post.created_at,
            status = post.status,
            like_count = post.like_count,
            dislike_count = post.dislike_count,
            comments = [] # A new post has zero comments.
        )

@router.get("/", response_model=list[schemas.PostResponse])
def get_book(
    topic: str | None = None,
    status: models.PostStatus | None = None,
    db: Session = Depends(get_db)
):
    '''
    Topic and status can be passed as optional query params: /posts?topic=Tech&status=1
    '''
    query = select(models.Post)
    if topic is not None:
        query = query.join(models.Post.topics).where(models.Topic.name == topic)
    if status is not None:
        query = query.where(models.Post.status == status.value)
    return db.scalars(query).all()

@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_book(post_id: int, db: Session = Depends(get_db)):
    query = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(
            joinedload(models.Post.author),
            selectinload(models.Post.topics),
            selectinload(models.Post.comments).joinedload(models.Comment.author),
        )
    )
    post = db.scalar(query)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {post_id} not found",
        )

    return post