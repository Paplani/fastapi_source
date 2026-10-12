# 게시글 삽입 : userId, title, body
# 게시글 조회 : userId, title, body, id

from pydantic import BaseModel, Field
from datetime import datetime


class UserResponse(BaseModel):
    user_id: int
    name: str


class CommentResponse(BaseModel):
    comment_id: int
    body: str
    user_id: int
    # 댓글 작성자 정보
    user: UserResponse
    board_id: int
    created_at: datetime


# 본문 최대 글자 수
# DB 컬럼은 VARCHAR2(2000 CHAR)지만 Oracle VARCHAR2는 최대 4000바이트까지만 저장
# 한글은 1글자 = 3바이트 → 약 1333자가 한계라서 여유 있게 1300자로 제한
CONTENTS_MAX_LENGTH = 1300


class BoardCreate(BaseModel):
    title: str = Field(
        min_length=1, max_length=100
    )  # Field를 쓰면 빈 문자열 ""를 막을수 있음
    contents: str = Field(min_length=1, max_length=CONTENTS_MAX_LENGTH)


class BoardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    contents: str | None = Field(
        default=None, min_length=1, max_length=CONTENTS_MAX_LENGTH
    )


class BoardResponse(BaseModel):
    id: int
    title: str
    contents: str
    user_id: int
    created_at: datetime
    # 댓글 목록
    comments: list[CommentResponse]
    # 게시글 작성자 이름
    user: UserResponse
    views: int


class BoardPageResponse(BaseModel):
    items: list[BoardResponse]
    total: int
    page: int
    size: int
    total_pages: int
    criteria: str
    keyword: str


class Comment(BaseModel):
    postId: int
    id: int
    name: str
    email: str
    body: str
