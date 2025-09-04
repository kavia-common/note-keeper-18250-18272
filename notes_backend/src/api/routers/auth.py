"""
Authentication routes: register and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db_session
from ..core.security import hash_password, verify_password, create_access_token
from ..models.models import User
from ..schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    summary="Register a new user",
    description="Create a new user account with email and password.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "User already exists"},
    },
    status_code=201,
)
# PUBLIC_INTERFACE
async def register_user(payload: RegisterRequest, db: AsyncSession = Depends(get_db_session)) -> UserOut:
    """Register a new user with an email and password."""
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user  # from_attributes makes ORM -> Pydantic possible


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate a user and return an access token.",
    responses={401: {"description": "Invalid credentials"}},
)
# PUBLIC_INTERFACE
async def login_user(payload: LoginRequest, db: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    """Authenticate the user and return a JWT access token."""
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, token_type="bearer")
