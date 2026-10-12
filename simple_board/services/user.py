from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    NameChange,
    EmailChange,
    PasswordChange,
)
from repository.models.user import User
from exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidPasswordException,
    SamePasswordException,
)
from core.security import has_password, verify_password
from utils.security import create_access_token
from schemas.user import Token

DUMMY_HASH = has_password("dummypassword")

# CRUD


# 회원가입
# 비밀번호 => 암호화
def register(db: Session, data: UserCreate):
    # 동일한 이메일로 가입된 정보가 있는가?
    # scalar : 단 하나의 값 => 행, 열이 교차하는 딱 한칸의 데이터
    # select * from board_users where email = "가입하려고 하는 이메일"
    existing_user = db.scalar(select(User).where(User.email == data.email))

    if existing_user:
        raise UserAlreadyExistsException

    # 가입된 정보가 없을 때 회원가입
    user = User(email=data.email, password=has_password(data.password), name=data.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 로그인
def authenticate(db: Session, data: UserLogin):

    existing_user = db.scalar(select(User).where(User.email == data.email))
    # 회원가입 정보가 없는 경우
    if existing_user is None:
        # Timing attack 방지 -> 일부러 시간 쓰기
        verify_password(data.password, DUMMY_HASH)
        raise UserNotFoundException

    # 비밀번호 검증 틀린 경우
    if not verify_password(data.password, existing_user.password):
        raise InvalidPasswordException

    access_token = create_access_token(data={"sub": str(existing_user.user_id)})

    return Token(access_token=access_token)


# 이름 변경
def update_name(db: Session, data: NameChange, user_id: int):
    # 수정할 대상 찾기
    user = db.get(User, user_id)

    if user is None:
        raise UserNotFoundException

    # 수정하기
    user.name = data.name
    db.commit()
    db.refresh(user)
    return user


# 이메일 변경
def update_email(db: Session, data: EmailChange, user_id: int):
    # 수정할 대상 찾기
    user = db.get(User, user_id)

    if user is None:
        raise UserNotFoundException

    # 수정하기
    user.email = data.email
    db.commit()
    db.refresh(user)
    return user


# 비밀번호 변경
def update_password(db: Session, data: PasswordChange, user_id: int):
    # 수정할 대상 찾기
    user = db.get(User, user_id)

    if user is None:
        raise UserNotFoundException

    # current_password 가 데이터 베이스 비밀번호랑 동일한가?
    # new_password 가 데이터 베이스 비밀번호와 동일한가?
    if not verify_password(data.current_password, user.password):
        raise InvalidPasswordException

    if verify_password(data.new_password, user.password):
        raise SamePasswordException

    # 수정하기
    user.password = has_password(data.new_password)
    db.commit()
    db.refresh(user)
    return user


# 현재 로그인된 사용자를 반환
def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFoundException

    return user
