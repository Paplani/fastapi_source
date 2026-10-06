from contextlib import asynccontextmanager
from fastapi import FastAPI
from repository.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """어플리케이션 전체의 시작과 종료 관리"""
    print("서버 시작")

    # 데이터베이스 초기화
    init_db()
    # LLM 쵝화
    # 벡터 DB 초기화

    yield

    print("서버 종료")

# yield 이전 → 서버가 요청을 받기 전 준비
# yield      → 준비를 마치고 서버가 요청을 처리하도록 넘김
# yield 이후 → 서버 종료 시 실행