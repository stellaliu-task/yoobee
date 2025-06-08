from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.database import get_session
from app.models import User, UserRole
from app.deps import get_current_active_user
from app.schemas.user import UserCreate, UserLogin, UserOut, UserResponse, Token
from app.utils import hash_password, verify_password, create_access_token

router = APIRouter(
    tags=["Auth"]
)
common_error_responses = {
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    422: {"description": "Validation Error"},
}

@router.post(
        "/register", 
        response_model=UserResponse, 
        status_code=status.HTTP_201_CREATED,
        responses={400: {"description": "Email already registered"}},)
async def register(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    result_email = await session.execute(select(User).where(User.email == user_in.email))
    user_email = result_email.scalar_one_or_none()
    if user_email:
        raise HTTPException(400, "Email already registered")

    result_name = await session.execute(select(User).where(User.name == user_in.name))
    user_name = result_name.scalar_one_or_none()
    if user_name:
        raise HTTPException(400, "Username already registered")

    
    hashed_pw = hash_password(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_pw,
                    name=user_in.name, role=user_in.role)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.post(
        "/login", 
        response_model=Token,
        responses={**common_error_responses},)
async def login(user_in: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(
        or_(User.email == user_in.email, User.name == user_in.name)
    ))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password")
    if user.blocked:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User blocked")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
