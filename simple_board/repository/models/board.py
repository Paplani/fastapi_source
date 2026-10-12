from repository.database import Base
from sqlalchemy import Identity, DateTime, String, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime


# id
# 제목, 내용, 작성자, 작성일, 수정일
class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(Identity(start=1, increment=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    contents: Mapped[str] = mapped_column(String(2000), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("board_users.user_id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    # 조회수 컬럼, server_default 값에는 문자열만 들어감
    views: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # 컬럼의 개념 아님(파이썬 객체간 연결) - User에서 Board에 접급할수 있게 하는 코드
    # => board.user.email 같은 코드로 user에 접근가능
    user: Mapped["User"] = relationship(back_populates="boards")
    # board.comments.count()
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="board",
        order_by="Comment.comment_id",  # 댓글 오래된 순으로 정렬해서 보여주기
        cascade="all, delete-orphan",  # 게시글 삭제 시 댓글도 함께 삭제
    )


# DB의 기본 규칙 : 자식이 있으면 부모 삭제 금지
# SQLALchemy가 먼저 움직임. Board.comments에 relationship이 있으면 SQLALchemy는 댓글의 board_id(외래키 연결)을 null로 바꿈
# 하지만 nullable=False 옵션에 의해 에러가 남.
# cascade="all, delete-orphan" => Null 로 바꾸지 않고 댓글을 먼저 delete 한 다음 글을 delete


class Board_Views(Base):
    __tablename__ = "board_views"

    # unique 제약조건. ex: 37번 글을, 1번 user가 읽음
    __table_args__ = (
        UniqueConstraint("board_id", "user_id", name="uq_board_view_user"),
    )

    id: Mapped[int] = mapped_column(Identity(start=1, increment=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("board_users.user_id"), nullable=False
    )
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
