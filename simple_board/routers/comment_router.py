from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from repository.database import get_db
from services.comment import comment_create, comment_delete, comment_update
from schemas.comment import CommentCreate, CommentUpdate
from exceptions.board import CommentNotFoundException


# 화면단 요청 처리

comment_router = APIRouter(tags=["Comments"])


@comment_router.post("", response_model=dict)
async def post_comment(data: CommentCreate, db: Session = Depends(get_db)):
    target_comment = comment_create(data, db=db)
    return {"message": f"댓글 {target_comment.comment_id}번이 생성되었습니다."}


@comment_router.put("/{comment_id}", response_model=dict)
async def put_comment(
    comment_id: int, data: CommentUpdate, db: Session = Depends(get_db)
):
    try:
        target_id = comment_update(comment_id=comment_id, data=data, db=db)
    except CommentNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수정할 댓글이 존재하지 않습니다.",
        )
    return {"message": f"댓글 {target_id}번이 수정되었습니다."}


@comment_router.delete("/{comment_id}", response_model=dict)
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    try:
        target_id = comment_delete(comment_id=comment_id, db=db)
    except CommentNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 댓글이 존재하지 않습니다.",
        )
    return {"message": f"댓글 {target_id}번이 삭제되었습니다."}
