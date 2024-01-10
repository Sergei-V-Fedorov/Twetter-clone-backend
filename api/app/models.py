from sqlalchemy import (
    ARRAY,
    TEXT,
    Column,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# Рассмотреть необходимость миграции моделей
associated_followers = Table(
    "associated_followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Sequence("user_id_seq"), primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False)
    api_key: Mapped[str] = mapped_column(nullable=False, unique=True)
    followers = relationship(
        "User",
        secondary=associated_followers,
        primaryjoin="User.id==associated_followers.c.following_id",
        secondaryjoin="User.id==associated_followers.c.follower_id",
        back_populates="following",
    )
    following = relationship(
        "User",
        secondary=associated_followers,
        primaryjoin="User.id==associated_followers.c.follower_id",
        secondaryjoin="User.id==associated_followers.c.following_id",
        back_populates="followers",
    )

    def __repr__(self):
        return f"User {self.name}"


associated_likes = Table(
    "associated_likes",
    Base.metadata,
    Column("tweet_id", Integer, ForeignKey("tweets.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(
        Sequence("media_id_seq"), primary_key=True, index=True
    )
    path: Mapped[str] = mapped_column(nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))

    def __repr__(self):
        return f"Media {self.path}"


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(
        Sequence("tweet_id_seq"), primary_key=True, index=True
    )
    content: Mapped[str] = mapped_column(TEXT, nullable=False)

    medias = relationship("Media", backref="tweets")
    attachments: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", backref="tweets")
    likes = relationship(
        "User",
        secondary=associated_likes,
        backref="likes",
    )

    def __repr__(self):
        return f"Tweet {self.id}"
