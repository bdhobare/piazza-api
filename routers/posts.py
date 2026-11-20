from fastapi import APIRouter, Depends

import models
import schemas
from security import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.BookResponse, status_code=201)
def create_post(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }