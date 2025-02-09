from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, index=True)

    # Relationship with rooms
    owned_rooms = relationship('Room', backref='owner', cascade="all, delete-orphan")


# Model for Shopping Items
class ShoppingItem(Base):
    __tablename__ = 'shopping_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True, nullable=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))


# Model for Rooms
class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))  # Link to User
    invite_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Relationships
    items = relationship('ShoppingItem', backref='room', cascade="all, delete-orphan")
    members = relationship('RoomUser', backref='room', cascade="all, delete-orphan")


# Model for Room-User
class RoomUser(Base):
    __tablename__ = 'room_users'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    # Relationship with User
    user = relationship('User', backref='room_users')

    # Ensure that a user cannot be added to the same room multiple times
    __table_args__ = (UniqueConstraint('room_id', 'user_id', name='unique_room_user'),)
