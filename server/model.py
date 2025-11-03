import datetime
from sqlalchemy import Enum as SQLAlchemyEnum
import enum
from typing import List, Optional, Tuple
import flask_login
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

from . import db

class FollowingAssociation(db.Model):
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

class User(flask_login.UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    proposals: Mapped[List["Proposal"]] = relationship(back_populates="user")
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
        username_parts = self.username.split()
        if len(username_parts) > 1:
            return username_parts[0][0].upper() + username_parts[-1][0].upper()
        return self.username[0].upper() if self.username else "?"

class ProposalStatus(enum.Enum):
    OPEN = 1
    CLOSED_TO_NEW = 2
    FINALIZED = 3
    CANCELLED = 4

class FinalizedError(Exception):
    pass

class Proposal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="proposals")
    title: Mapped[Optional[str]] = mapped_column(String(512), default="")
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[ProposalStatus] = mapped_column(SQLAlchemyEnum(ProposalStatus), default=ProposalStatus.OPEN)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, default=1, nullable=False)
    messages: Mapped[List["Message"]] = relationship(back_populates="proposal")
    participants: Mapped[List["ProposalParticipant"]] = relationship(back_populates="proposal")

    dates: Mapped[List[Tuple[datetime.datetime, datetime.datetime]]] = mapped_column(JSON, default=list, nullable=True)
    final_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    budget: Mapped[Optional[float]] = mapped_column(Float, default=None, nullable=True)
    accommodation: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)
    transportation: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)
    activities: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)
    departure_locations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=True)
    final_departure_location: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)
    destinations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=True)

    finalized_flags: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=lambda: {}
    )

    def is_final(self, field_name: str) -> bool:
        if self.finalized_flags is None:
            return False
        return bool(self.finalized_flags.get(field_name, False))

    def finalize(self, field_name: str, by_user: Optional[int] = None):
        self.finalized_flags[field_name] = {
            "final": True,
            "at": datetime.datetime.now(datetime.timezone.utc)
        }

    def unfinalize(self, field_name: str):
        self.finalized_flags.pop(field_name, None)

    @validates("dates", "final_date", "budget", "accommodation", "transportation", "activities", "departure_locations", "final_departure_location", "destinations")
    def _validate_not_final(self, key, value):
        if self.is_final(key):
            raise FinalizedError(f"Field '{key}' is finalized and cannot be modified.")
        return value
    
    def has_permission(self, user, min_role) -> bool:
        for participant in self.participants:
            if participant.user_id == user.id:
                return participant.permission.value >= min_role.value
        return False


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    content: Mapped[str] = mapped_column(String(1024))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposal.id"))
    proposal: Mapped["Proposal"] = relationship(back_populates="messages")
    response_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("message.id"))
    response_to: Mapped[Optional["Message"]] = relationship(
        back_populates="responses", remote_side=[id]
    )
    responses: Mapped[List["Message"]] = relationship(
        back_populates="response_to"
    )

class ProposalParticipantRole(enum.Enum):
    VIEWER = 1
    EDITOR = 2
    ADMIN = 3

class ProposalParticipant(db.Model):
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposal.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    proposal: Mapped["Proposal"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
    joined_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    permission: Mapped[ProposalParticipantRole] = mapped_column(SQLAlchemyEnum(ProposalParticipantRole), default=ProposalParticipantRole.VIEWER)

class Meetup(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposal.id"))
    proposal: Mapped["Proposal"] = relationship()
    location: Mapped[str] = mapped_column(String(256))
    time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[Optional[str]] = mapped_column(String(512), default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by_user: Mapped["User"] = relationship()
    participants: Mapped[List["MeetupParticipant"]] = relationship(back_populates="meetup")

class MeetupParticipant(db.Model):
    meetup_id: Mapped[int] = mapped_column(ForeignKey("meetup.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    meetup: Mapped["Meetup"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
