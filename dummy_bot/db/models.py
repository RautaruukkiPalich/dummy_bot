from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


# class Pokak(Base):
#     __tablename__ = 'pokaks'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = relationship(ForeignKey("users.id"))
#     created_at: Mapped[datetime] = mapped_column(default=datetime.now)
#
#     user: Mapped["User"] = relationship("User", back_populates="pokak")
#
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='pokak_id'),
#     )


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_on: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    # media = relationship("Media", back_populates="group")
    # user = relationship("User", back_populates="group")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='group_id'),
    )


class Media(Base):
    __tablename__ = 'medias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    media_unique_id = Column(String(250), default="")
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    group = relationship("Group", back_populates="media")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='media_id'),
    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"))
    username = Column(String(250), default="", nullable=False)
    full_name = Column(String(250), default=" ")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    pokak = relationship("Pokak", back_populates="user")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_id'),
        UniqueConstraint("chat_id", "group_id", name="chat_in_group"),
    )


class Pokak(Base):
    __tablename__ = 'pokaks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(), default=datetime.now)

    user = relationship("User", back_populates="pokak")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pokak_id'),
    )
