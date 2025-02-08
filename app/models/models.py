from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Model for Shopping Items
class ShoppingItem(Base):
    __tablename__ = 'shopping_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

# Model for Rooms
class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer)
    invite_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Relationships
    items = relationship('ShoppingItem', backref='room')
    members = relationship('RoomUser', backref='room')


# Model for Room-User
class RoomUser(Base):
    __tablename__ = 'room_users'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    user_id = Column(Integer)

    # Ensure that a user cannot be added to the same room multiple times
    __table_args__ = (UniqueConstraint('room_id', 'user_id', name='unique_room_user'),)
