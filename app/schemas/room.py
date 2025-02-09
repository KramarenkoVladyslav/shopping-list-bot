from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# Base schema for Room (used for inheritance)
class RoomBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=30, description="Name of the room")


# Schema for creating a new room
class RoomCreate(RoomBase):
    pass  # No changes needed, inherits validation from RoomBase


# Schema for updating an existing room
class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=30, description="Updated name of the room")


# Schema for API response
class RoomResponse(RoomBase):
    id: int
    owner_id: int
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True


    # Schema for returning a list of rooms
class RoomListResponse(BaseModel):
    rooms: List[RoomResponse] = Field(..., description="List of rooms")

    class Config:
        from_attributes = True