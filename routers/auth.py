from fastapi import APIRouter
from models.user.requests import UserLoginRequest, UserRegisterRequest

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
