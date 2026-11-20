from fastapi import APIRouter, Depends

import models
from security import get_current_user

router = APIRouter()


@router.get("/me")
def get_profile(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }