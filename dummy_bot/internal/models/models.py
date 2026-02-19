from datetime import datetime

from sqlalchemy import (
    PrimaryKeyConstraint,
    UniqueConstraint,
    ForeignKey, BigInteger,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_on: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='group_id'),
    )


class Media(Base):
    __tablename__ = 'medias'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    group: Mapped["Group"] = relationship(foreign_keys=[group_id])
    media_unique_id: Mapped[str] = mapped_column(nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='media_id'),
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    group: Mapped["Group"] = relationship(foreign_keys=[group_id])
    username: Mapped[str | None] = mapped_column(default="", nullable=True)
    fullname: Mapped[str] = mapped_column(default=" ", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_id'),
        UniqueConstraint("chat_id", "group_id", name="chat_in_group"),
    )

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


class Pokak(Base):
    __tablename__ = 'pokaks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pokak_id'),
    )
