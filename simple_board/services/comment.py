from sqlalchemy.orm import Session
from schemas.comment import CommentCreate, CommentUpdate
from repository.models.comments import Comment
from repository.models.user import User
from exceptions.board import CommentNotFoundException, CommentPermissionException


# CURD


# 댓글 등록
def comment_create(data: CommentCreate, db: Session, current_user: User):
    comment = Comment(
        body=data.body, user_id=current_user.user_id, board_id=data.board_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


# 댓글 수정
def comment_update(comment_id: int, data: CommentUpdate, db: Session, user_id: int):
    comment = db.get(Comment, comment_id)  # 댓글 하나 가져오기
    if comment is None:
        raise CommentNotFoundException

    if comment.user_id != user_id:
        raise CommentPermissionException

    if data.body is not None:
        comment.body = data.body

    db.commit()
    return comment_id


# 댓글 삭제
def comment_delete(comment_id: int, db: Session, user_id: int):
    target_comment = db.get(Comment, comment_id)  # 타깃 댓글 가져오기

    if target_comment is None:
        raise CommentNotFoundException

    if target_comment.user_id != user_id:
        raise CommentPermissionException

    db.delete(target_comment)
    db.commit()
    return comment_id
