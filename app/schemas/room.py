from typing import Optional, List

from pydantic import BaseModel


class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None


class RoomResponse(RoomBase):
    id: int
    owner_id: int
    invite_code: str

    class Config:
        orm_mode = True


class RoomListResponse(BaseModel):
    rooms: List[RoomResponse]