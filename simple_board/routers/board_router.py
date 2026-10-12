from fastapi import APIRouter, HTTPException, status
from schemas.board import BoardCreate, BoardUpdate, BoardPageResponse, BoardResponse
from services.board import (
    create,
    update,
    select_all,
    select_one,
    delete,
    recentPosts,
    update_views,
)
from fastapi import Depends
from sqlalchemy.orm import Session
from repository.database import get_db
from exceptions.board import BoardNotFoundException, BoardPermissionException
from exceptions.user import UserCredentialsException
from core.dependencies import get_current_user
from repository.models.user import User

board_router = APIRouter(tags=["Boards"])


# 전체 조회 : GET+ http://localhost:8000/boards
@board_router.get("", response_model=BoardPageResponse)
async def get_boards(
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    criteria: str = "",
    keyword: str = "",
):
    result = select_all(db=db, page=page, size=size, criteria=criteria, keyword=keyword)
    return result


# 최신글 조회 + GET : http://localhost:8000/boards/recents
@board_router.get("/recents", response_model=list[BoardResponse])
async def get_boards_recent(db: Session = Depends(get_db)):
    target_boards = recentPosts(db=db)
    return target_boards


# 하나만 조회 : GET+ http://localhost:8000/boards/1
# 로그인된 사용자만 조회 가능하게끔
@board_router.get("/{id}", response_model=BoardResponse)
async def get_board(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),  # 토큰값이 안오면 바로 에러남 -> 로그인한 사람만 게시글 볼수 있도록.
):
    try:
        board = select_one(db=db, id=id)
        update_views(board=board, db=db, current_user=current_user)
    except BoardNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="찾는 board가 없습니다."
        )
    return board


# 하나만 수정 : PUT+ http://localhost:8000/boards/1 + 수정데이터
@board_router.put("/{id}", response_model=dict)
async def put_board(
    id: int,
    update_board: BoardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        target_id = update(
            db=db, id=id, data=update_board, user_id=current_user.user_id
        )
    except BoardNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="찾는 board가 없습니다."
        )
    except BoardPermissionException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 글만 수정할 수 있습니다.",
        )
    return {"message": f"{target_id}번이 수정되었습니다."}


# 하나 추가 : POST+ http://localhost:8000/boards + 삽입할 내용
@board_router.post("", response_model=dict)
async def post_board(
    data: BoardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # boards -> board
    try:
        new_board = create(db=db, data=data, current_user=current_user)
    except UserCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자입니다.",
        )

    return {"message": f"{new_board.id}번이 삽입되었습니다"}


# 하나만 삭제 : DELETE+ http://localhost:8000/boards/1
@board_router.delete("/{id}", response_model=dict)
async def delete_board(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        target_id = delete(db=db, id=id, user_id=current_user.user_id)
    except BoardNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="찾는 board가 없습니다."
        )
    except BoardPermissionException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 글만 삭제할 수 있습니다.",
        )
    return {"message": f"{target_id}번이 삭제되었습니다."}


# # 댓글 조회 : GET+ http://localhost:8000/boards/1/comments
# @board_router.get("/{id}/comments", response_model=list[Comment])
# async def get_board_comment(id: int):
#     return []
