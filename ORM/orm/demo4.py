from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, func, select, and_, or_, not_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


class Base(DeclarativeBase):
    created_time: Mapped[datetime] = mapped_column(default=datetime.now,comment="创建时间")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    age: Mapped[Optional[int]] = mapped_column(default=None)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    views: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
