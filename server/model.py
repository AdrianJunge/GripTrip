import datetime
import json
from sqlalchemy import Enum as SQLAlchemyEnum
import enum
from typing import List, Optional, Tuple
import flask_login
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
import pycountry

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
    country_code: Mapped[str] = mapped_column(String(3), nullable=False)
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
    def country(self):
        country = pycountry.countries.get(alpha_3=self.country_code)
        return country.name if country else "Unknown"

    @property
    def avatar(self):
        username_parts = self.username.split()
        if len(username_parts) > 1:
            return username_parts[0][0].upper() + username_parts[-1][0].upper()
        return self.username[0].upper() if self.username else "?"

    def is_following(self, user):
        return user in self.following

class ProposalStatus(enum.Enum):
    OPEN = 1
    CLOSED_TO_NEW = 2
    FINALIZED = 3
    CANCELLED = 4

class FinalizedError(Exception):
    pass

class Proposal(db.Model):
    # Basic info - mandatory
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="proposals")
    title: Mapped[Optional[str]] = mapped_column(String(512), default="", nullable=False)
    timestamp_raw: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    status: Mapped[ProposalStatus] = mapped_column(SQLAlchemyEnum(ProposalStatus), default=ProposalStatus.OPEN)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    messages: Mapped[List["Message"]] = relationship(back_populates="proposal")
    participants: Mapped[List["ProposalParticipant"]] = relationship(back_populates="proposal")

    # Trip details - optional/tentative
    budget: Mapped[Optional[float]] = mapped_column(Float, default=None, nullable=True)
    accommodation: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)
    transportation: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)

    activities: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=True)
    dates: Mapped[List[Tuple[datetime.datetime, datetime.datetime]]] = mapped_column(JSON, default=list, nullable=True)
    departure_locations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=True)
    destinations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=True)
    
    final_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    final_departure_location: Mapped[Optional[str]] = mapped_column(String(256), default=None, nullable=True)

    finalized_flags: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=lambda: {}
    )

    @property
    def timestamp(self):
        return self.timestamp_raw.replace(tzinfo=datetime.timezone.utc)

    @property
    def participant_count(self):
        return len(self.participants)

    def is_final(self, field_name: str) -> bool:
        if self.finalized_flags is None:
            return False
        return bool(self.finalized_flags.get(field_name, False))

    def finalize(self, field_name: str, by_user: Optional[int] = None):
        self.finalized_flags[field_name] = {
            "final": True,
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    def unfinalize(self, field_name: str):
        self.finalized_flags.pop(field_name, None)

    @validates("dates", "budget", "accommodation", "transportation", "activities", "departure_locations", "destinations")
    def _validate_attributes(self, key, value):
        if self.is_final(key) and value != getattr(self, key):
            raise FinalizedError(f"Field '{key}' is finalized and cannot be modified.")
        
        if key == "budget":
            try:
                if value is not None:
                    value = float(value)
            except ValueError:
                raise ValueError("Budget must be a number.")
            if value is not None and value < 0:
                raise ValueError("Budget cannot be negative.")

        if key == "max_participants":
            try:
                if value is not None:
                    value = int(value)
            except ValueError:
                raise ValueError("Maximum participants must be an integer.")
            if value is not None and value < 1:
                raise ValueError("Maximum participants must be at least 1.")

        if key == "dates":
            for date_range in value:
                if (not isinstance(date_range, tuple) or len(date_range) != 2 or
                    not all(isinstance(d, str) for d in date_range)):
                    raise ValueError("Each date range must be a tuple of two ISO format datetime strings.")
                start = datetime.datetime.fromisoformat(date_range[0])
                end = datetime.datetime.fromisoformat(date_range[1])
                if start >= end:
                    raise ValueError("In each date range, start date must be before end date.")
                
        if key == "accommodation":
            pass

        if key == "transportation":
            pass

        if key == "activities" or key == "destinations" or key == "departure_locations":
            if not isinstance(value, list):
                raise ValueError("Must be a list of strings.")

        return value
    
    def has_permission(self, user, min_role) -> bool:
        for participant in self.participants:
            if participant.user_id == user.id:
                return participant.permission.value >= min_role.value
        return False

    def get_participant(self, user):
        for participant in self.participants:
            if participant.user_id == user.id:
                return participant
        return None

    def get_user_role(self, user):
        p = self.get_participant(user)
        return p.permission if p is not None else None


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship()
    content: Mapped[str] = mapped_column(String(1024))
    timestamp_raw: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
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

    # for some reason mysql doesn't store timezone info properly so we need to ensure it's aware
    @property
    def timestamp(self):
        return self.timestamp_raw.replace(tzinfo=datetime.timezone.utc)


class ProposalParticipantRole(enum.Enum):
    VIEWER = 1
    EDITOR = 2
    ADMIN = 3

class ProposalParticipant(db.Model):
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposal.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    proposal: Mapped["Proposal"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
    joined_at_raw: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    permission: Mapped[ProposalParticipantRole] = mapped_column(SQLAlchemyEnum(ProposalParticipantRole), default=ProposalParticipantRole.VIEWER)

    @property
    def joined_at(self):
        return self.joined_at_raw.replace(tzinfo=datetime.timezone.utc)

class Meetup(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposal.id"))
    proposal: Mapped["Proposal"] = relationship()
    location: Mapped[str] = mapped_column(String(256))
    date_raw: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    description: Mapped[Optional[str]] = mapped_column(String(512), default="")
    created_at_raw: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by_user: Mapped["User"] = relationship()
    participants: Mapped[List["MeetupParticipant"]] = relationship(back_populates="meetup")

    @property
    def date(self):
        return self.date_raw.replace(tzinfo=datetime.timezone.utc)

    @property
    def created_at(self):
        return self.created_at_raw.replace(tzinfo=datetime.timezone.utc)

class MeetupParticipant(db.Model):
    meetup_id: Mapped[int] = mapped_column(ForeignKey("meetup.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    meetup: Mapped["Meetup"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
