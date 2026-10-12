from fastapi import APIRouter, HTTPException, status
from services.user import (
    register,
    authenticate,
    update_name,
    update_email,
    update_password,
)
from schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    NameChange,
    PasswordChange,
    EmailChange,
)
from sqlalchemy.orm import Session
from fastapi import Depends
from repository.database import get_db
from exceptions.user import (
    UserAlreadyExistsException,
    InvalidPasswordException,
    UserNotFoundException,
    SamePasswordException,
)
from schemas.user import Token
from repository.models.user import User
from core.dependencies import get_current_user
from fastapi.exceptions import RequestValidationError

auth_router = APIRouter(tags=["Users"])


# 회원가입 /auth + post
# 로그인 /auth/login + post
# 비밀번호수정 /auth/1/password + patch
# 이름수정 /auth/1/name + patch
# 이메일수정 /auth/1/email + patch


@auth_router.get("/me", response_model=UserResponse)
async def read_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user


@auth_router.post("", response_model=dict)
async def post_signup(data: UserCreate, db: Session = Depends(get_db)) -> dict:
    try:
        user = register(data=data, db=db)
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 이메일입니다. 다시 시도해주세요",
        )
    return {"message": "회원가입이 완료되었습니다.", "user_id": user.user_id}


@auth_router.post("/login", response_model=Token)
async def post_signin(data: UserLogin, db: Session = Depends(get_db)) -> Token:
    try:
        token = authenticate(data=data, db=db)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="일치하는 이메일이 없습니다.",
        )
    except InvalidPasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 일치하지 않습니다.",
        )
    return token


@auth_router.patch("/{user_id}/name", response_model=dict)
async def patch_name(
    user_id: int, data: NameChange, db: Session = Depends(get_db)
) -> dict:
    try:
        update_name(data=data, db=db, user_id=user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일치하는 이메일이 없습니다."
        )
    return {"message": "이름이 변경되었습니다"}


@auth_router.patch("/{user_id}/email", response_model=dict)
async def patch_email(
    user_id: int, data: EmailChange, db: Session = Depends(get_db)
) -> dict:
    try:
        update_email(user_id=user_id, data=data, db=db)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일치하는 이메일이 없습니다."
        )
    return {"message": "이메일이 변경되었습니다"}


@auth_router.patch("/{user_id}/password", response_model=dict)
async def patch_password(
    user_id: int, data: PasswordChange, db: Session = Depends(get_db)
) -> dict:
    try:
        update_password(user_id=user_id, data=data, db=db)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저 정보가 없습니다. 다시 입력해주세요",
        )
    except InvalidPasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호를 다시 입력해주세요.",
        )
    except SamePasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="기존과 다른 새로운 비밀번호를 입력해주세요.",
        )
    return {"message": "비밀번호가 변경되었습니다"}
