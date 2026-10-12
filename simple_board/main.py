from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.board_router import board_router
from routers.user_router import auth_router
from core.lifespan import lifespan
from routers.comment_router import comment_router
from exceptions.user import UserCredentialsException

app = FastAPI(lifespan=lifespan, title="Board & User Project", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 어떤 출처의 요청을 허용할 것인가?
    allow_credentials=True,  # 쿠키나 인증정보를 포함한 요청을 허용할 것인가?
    allow_methods=["*"],  # 어떤 메소드를 허용할 것인가? (post, get, put, patch, delete)
    allow_headers=["*"],  # 요청에서 사용할 수 있는 헤더정보
)

# router 설정 - 개별 라우터 생성 후 포함
app.include_router(board_router, prefix="/boards")
app.include_router(auth_router, prefix="/auth")
app.include_router(comment_router, prefix="/comments")


# 의존성 안에서 발생한 예외(의존성이 의존성을 부르는 구조(get_current_user → HTTPBearer, get_db)이고, FastAPI가 순서대로 실행해줌)
# 위의 예외들은 라우터 함수의 try/except 들어가기 전에 터짐. 
# 라우터에서 잡을수 없으니 처리하지 않으면 500 에러가 생김. 그래서 앱 전체에 등록.
@app.exception_handler(UserCredentialsException)
async def credentials_handler(request: Request, exc: UserCredentialsException):
    return JSONResponse(
        status_code=401,
        content={"detail": "인증 정보가 유효하지 않습니다."},
        headers={"WWW-Authenticate": "Bearer"},
    )
