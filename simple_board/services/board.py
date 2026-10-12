from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from repository.models.board import Board, Board_Views
from repository.models.comments import Comment
from repository.models.user import User
from schemas.board import BoardCreate, BoardUpdate
from exceptions.board import BoardNotFoundException
from exceptions.board import BoardPermissionException
import math

# CURD


# 조회수 증가
def update_views(db: Session, board: Board, current_user: User):
    # Boards 테이블의 views + 1
    # Board_Views 테이블에 insert () => 동일한 값이 존재하는지 확인

    stmt = select(Board_Views).where(
        Board_Views.board_id == board.id, Board_Views.user_id == current_user.user_id
    )
    view = db.scalar(stmt)

    if view is None:
        board.views += 1

        board_view = Board_Views(board_id=board.id, user_id=current_user.user_id)
        db.add(board_view)
        db.commit()


def create(db: Session, data: BoardCreate, current_user: User):
    # 스키마 => 테이블 연결 모델
    board = Board(
        title=data.title, contents=data.contents, user_id=current_user.user_id
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def update(db: Session, id: int, data: BoardUpdate, user_id):
    # 수정할 대상 찾기
    target_board = db.get(Board, id)

    if target_board is None:  # 먼저 존재 확인 -> 404
        raise BoardNotFoundException

    if target_board.user_id != user_id:  # 로그인 사용자 == 작성자 인가 검증 -> 403
        raise BoardPermissionException

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


# 댓글 있는 경우 board 하나 조회 + 조회수 하나씩 증가
def select_one(db: Session, id: int):
    stmt = (
        select(Board)
        .options(
            selectinload(Board.user),  # 게시글 작성자 정보 가져오기
            selectinload(Board.comments).selectinload(
                Comment.user
            ),  # 댓글 + 댓글 작성자
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


# page, size 이용하는 전체조회 + 검색
def select_all(db: Session, page: int, size: int, criteria: str, keyword: str):

    query = db.query(Board)  # 쿼리 정의 (데이터베이스의 Board 테이블을 조회할것임)

    if keyword:
        if criteria == "tc":  # 제목 + 작성자
            query = query.filter(
                Board.title.contains(keyword) | Board.contents.contains(keyword)
            )
        elif criteria == "t":  # 제목
            query = query.filter(Board.title.contains(keyword))
        # 작성자 => 작성자 이름이 boards 테이블에 없음, 작성자 이름은 board_users에 있음.
        # 따라서 두 테이블을 JOIN 해야 이름으로 검색가능.
        elif criteria == "w":
            query = query.join(Board.user).filter(User.name.contains(keyword))

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
        "criteria": criteria,
        "keyword": keyword,
    }


# 삭제
def delete(db: Session, id: int, user_id: int):
    target_board = db.get(Board, id)

    if target_board is None:
        raise BoardNotFoundException

    if target_board.user_id != user_id:
        raise BoardPermissionException

    db.delete(target_board)
    db.commit()
    return id
