import datetime
from typing import List, Optional
import flask_login

from sqlalchemy import String, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import db

class FollowingAssociation(db.Model):
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

class User(flask_login.UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(256))
    # posts: Mapped[List["Post"]] = relationship(back_populates="user")
    bio: Mapped[Optional[str]] = mapped_column(String(256), default="")
    following: Mapped[List["User"]] = relationship(
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.follower_id == id,
        secondaryjoin=FollowingAssociation.followed_id == id,
        back_populates="followers",
    )
    followers: Mapped[List["User"]] = relationship(
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.followed_id == id,
        secondaryjoin=FollowingAssociation.follower_id == id,
        back_populates="following",
    )

    @property
    def avatar(self):
        name_parts = self.name.split()
        if len(name_parts) > 1:
            return name_parts[0][0].upper() + name_parts[-1][0].upper()
        return self.name[0].upper() if self.name else "?"
    
    @property
    def username(self):
        return self.name.lower().replace(" ", "") if self.name else ""
    
    # def get_post_count(self):
    #     return len(self.posts)
    
    def get_follower_count(self):
        return len(self.followers)
    
    def get_following_count(self):
        return len(self.following)

    def is_following(self, user):
        return user in self.following

# class Post(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship(back_populates="posts")
#     caption: Mapped[Optional[str]] = mapped_column(String(512), default="")
#     timestamp: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True), server_default=func.now()
#     )

# class Message(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship()
#     content: Mapped[str] = mapped_column(String(1024))
#     timestamp: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True), server_default=func.now()
#     )
#     response_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post.id"))
#     response_to: Mapped["Post"] = relationship(
#         back_populates="responses", remote_side=[id]
#     )
#     responses: Mapped[List["Post"]] = relationship(
#         back_populates="response_to", remote_side=[response_to_id]
#     )

#     def get_num_replies(self):
#         return len(self.responses)
