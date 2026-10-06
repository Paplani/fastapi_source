from sqlalchemy.orm import Session
from schemas.comment import CommentCreate, CommentUpdate
from repository.models.comments import Comment
from exceptions.board import CommentNotFoundException

# CURD


# 댓글 등록
def comment_create(data: CommentCreate, db: Session):
    comment = Comment(body=data.body, user_id=data.user_id, board_id=data.board_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


# 댓글 수정
def comment_update(comment_id: int, data: CommentUpdate, db: Session):
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise CommentNotFoundException

    if data.body is not None:
        comment.body = data.body

    db.commit()
    return comment_id


# 댓글 삭제
def comment_delete(comment_id: int, db: Session):
    target_comment = db.get(Comment, comment_id)

    if target_comment is None:
        raise CommentNotFoundException

    db.delete(target_comment)
    db.commit()
    return comment_id
