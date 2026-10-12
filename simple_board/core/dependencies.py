from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from utils.security import verify_access_token
from repository.database import get_db
from repository.models.user import User
from exceptions.user import UserNotFoundException, UserCredentialsException
from services.user import get_user

# form submit
# Swagger의 Authorize 버튼이 이 주소로 로그인 요청을 보냄
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# data 만 주고받을때
security = HTTPBearer()


# get_current_user가 HTTPException이 아니라 커스텀 예외를 던지고 있음.
# 이 예외는 router의 try/except까지 오지 않음 (의존성 단계에서 발생함), 처리해주지 않으면 500 에러가 남.
# 이를 방지하기 위헤 main의 app.exception_handler로 관리.
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = verify_access_token(token)  # 토큰 검사
    user_id = payload.get("sub")

    if user_id is None:
        raise UserCredentialsException

    return get_user(db=db, user_id=user_id)
