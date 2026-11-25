from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select
from datetime import datetime, timezone

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
            like_count = 0,
            dislike_count = 0,
            expires_at = request.expires_at.astimezone(timezone.utc)
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
            author = schemas.UserResponse(
                id = current_user.id,
                name = current_user.name,
                email = current_user.email
            ),
            title=post.title,
            body = post.body,
            topics=request_topics,
            created_at=post.created_at,
            expires_at=post.expires_at,
            status = post.status,
            like_count = post.like_count,
            dislike_count = post.dislike_count,
            comments = [] # A new post has zero comments.
        )

@router.get("/", response_model=list[schemas.PostResponse], status_code=200)
def get_posts(
    topic: str | None = None,
    status: models.PostStatus | None = None,
    db: Session = Depends(get_db)
):
    '''
    Get all posts. Topic and status can be passed as optional query params: /posts?topic=Tech&status=Expired
    '''
    now_utc = datetime.now(timezone.utc).timestamp()
    query = select(models.Post)
    if topic is not None:
        query = query.join(models.Post.topics).where(models.Topic.name == topic)
    if status is None:
        return db.scalars(query).all()
    if status not in models.PostStatus:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if status == models.PostStatus.Expired:
        # Expired posts are those expires_at has passed
        query = query.where(now_utc >= models.Post.expires_at)
    else:
        # Live posts are those that expires_at has not passed.
        query = query.where(now_utc < models.Post.expires_at)

    return db.scalars(query).all()

@router.get("/{post_id}", response_model=schemas.PostResponse, status_code=200)
def get_post(post_id: int, db: Session = Depends(get_db)):
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

@router.put("/{post_id}/reaction", response_model=schemas.ReactionResponse, status_code=200)
def put_reaction(post_id: int, request: schemas.ReactionCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    Set or replace the current user’s reaction on a post
    '''
    # Get the post and check status
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if post is not None:
        raise HTTPException(status_code=404, detail="Post does not exist.")
    if post.status ==  schemas.PostStatus.Expired:
        raise HTTPException(status_code=409, detail="Post is expired.")
    # Determine if post is expired based on the current timestamp
    if datetime.now(timezone.utc) >= post.expires_at:
        post.status = schemas.PostStatus.Expired
        db.commit()
        raise HTTPException(status_code=409, detail="Post is expired.")
    # Authors cannot like or dislike their own posts.
    if post.author_id == current_user.id:
        raise HTTPException(status_code=403, detail="Authors cannot like or dislike their own posts.")
    # Get the reaction type, check if the user has already reacted, and update the counts accordingly
    existing_reaction = db.query(models.Reaction).filter(
        models.Reaction.post_id == post_id,
        models.Reaction.author_id == current_user.id
    ).first()
    
    # If the user has not reacted yet, we need to create a new reaction and update the counts accordingly
    if existing_reaction is None:
        new_reaction = models.Reaction(
            author_id=current_user.id,
            post_id=post_id,
            reaction=request.value
        )
        db.add(new_reaction)
        # Update the counts based on the new reaction
        if request.value == schemas.Reaction.Like:
            post.like_count += 1
        else:
            post.dislike_count += 1
        db.commit()
        return schemas.ReactionResponse(
            post_id=post_id,
            likes=post.like_count,
            dislikes=post.dislike_count,
            updated_at=new_reaction.updated_at
        )

    if existing_reaction.reaction == request.value:
        # user is trying to set the same reaction, return the existing reaction
        return schemas.ReactionResponse(
            post_id=post_id,
            likes=post.like_count,
            dislikes=post.dislike_count,
            updated_at=existing_reaction.updated_at
        )
    # User is changing their reaction, we need to update the counts accordingly
    if existing_reaction.reaction == schemas.Reaction.Like:
        post.like_count -= 1
    else:
        post.dislike_count -= 1
    # Update the existing reaction to the new value
    existing_reaction.reaction = request.value
    existing_reaction.updated_at = int(datetime.now(timezone.utc).timestamp())
    # Update the counts based on the new reaction
    if request.value == schemas.Reaction.Like:
        post.like_count += 1
    else:
        post.dislike_count += 1
    db.commit()
    return schemas.ReactionResponse(
        post_id=post_id,
        likes=post.like_count,
        dislikes=post.dislike_count,
        updated_at=existing_reaction.updated_at
    )

@router.post("/{post_id}/comments", response_model=schemas.CommentResponse, status_code=201)
def post_comment(post_id: int, request: schemas.CommentCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    Add a comment to a post that is not Expired.
    '''
    # Get the post and check status
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if post is not None:
        raise HTTPException(status_code=404, detail="Post does not exist.")
    if post.status ==  schemas.PostStatus.Expired:
        raise HTTPException(status_code=409, detail="Post is expired.")
    # Determine if post is expired based on the current timestamp
    if datetime.now(timezone.utc) >= post.expires_at:
        post.status = schemas.PostStatus.Expired
        db.commit()
        raise HTTPException(status_code=409, detail="Post is expired.")
    
    comment = models.Comment(
        author_id=current_user.id,
        post_id=post_id,
        body=request.body,
    )
    db.add(comment)
    db.commit()
    return schemas.CommentResponse(
        id=comment.id,
        author=schemas.UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email
        ),
        post_id=post_id,
        body=comment.body,
        created_at=comment.created_at
    )