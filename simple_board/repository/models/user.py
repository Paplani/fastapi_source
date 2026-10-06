from repository.database import Base
from sqlalchemy import Identity, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

# user_id : pk
# email : unique
# password
# name
# 가입일


class User(Base):
    __tablename__ = "board_users"

    user_id: Mapped[int] = mapped_column(
        Identity(start=1, increment=1), primary_key=True
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    # 한명의 유저가 작성한 글들을 리스트로 받아볼수 있어야함
    # => user.boards.title 같은 코드로 board에 접근가능
    boards: Mapped[list["Board"]] = relationship(back_populates="user")
    # user.comments
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")

    # 하나쪽은 list[...], 여러개 쪽은 단일 객체
    # back_populates : 짝의 이름을 서로 적는것 - 상대 클래스에 있는 속성 이름