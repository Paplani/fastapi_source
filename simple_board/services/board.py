from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from repository.models.board import Board
from repository.models.comments import Comment
from schemas.board import BoardCreate, BoardUpdate
from exceptions.board import BoardNotFoundException
import math

# CURD


def create(db: Session, data: BoardCreate):
    # 스키마 => 테이블 연결 모델
    board = Board(title=data.title, contents=data.contents, user_id=data.user_id)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def update(db: Session, id: int, data: BoardUpdate):
    # 수정할 대상 찾기
    target_board = db.get(Board, id)

    if target_board is None:
        raise BoardNotFoundException

    # title만 수정 / contents만 수정 / title, contents 둘다 수정
    if data.title is not None:
        target_board.title = data.title

    if data.contents is not None:
        target_board.contents = data.contents

    db.commit()
    return id


# id와 일치하는 board 하나 조회 -> 댓글 없는 경우
# def select_one(db: Session, id: int):
#     target_board = db.get(Board, id)

#     if target_board is None:
#         raise BoardNotFoundException

#     return target_board


# 댓글 있는 경우 board 하나 조회
def select_one(db: Session, id: int):
    stmt = (
        select(Board)
        .options(
            selectinload(Board.user),     # 게시글 작성자 정보 가져오기
            selectinload(Board.comments).selectinload(Comment.user),    # 댓글 + 댓글 작성자
        )
        .where(Board.id == id)
    )

    target_board = db.scalar(stmt)

    if target_board is None:
        raise BoardNotFoundException

    return target_board


# 최신 게시글 4개만 뽑기
def recentPosts(db: Session):
    return db.query(Board).order_by(Board.id.desc()).limit(4).all()


# page, size 이용하는 전체조회
def select_all(db: Session, page: int, size: int):

    query = db.query(Board)  # 쿼리 정의 (데이터베이스의 Board 테이블을 조회할것임)

    # 전체 개수
    total = query.count()
    offset = (page - 1) * size
    # select * from boards order by id desc limit 20
    boards = query.order_by(Board.id.desc()).offset(offset).limit(size).all()
    total_pages = math.ceil(total / size)

    return {
        "items": boards,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages,
    }


# 삭제
def delete(db: Session, id: int):
    target_board = db.get(Board, id)

    if target_board is None:
        raise BoardNotFoundException

    db.delete(target_board)
    db.commit()
    return id
