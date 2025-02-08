from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.room import RoomResponse, RoomCreate
from app.core.database import get_db
from app.repositories.room import create_room, get_user_rooms, update_room, delete_room
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/rooms", tags=["Room routes"])

@router.post("/", response_model=RoomResponse)
async def create_new_room(room_data: RoomCreate, db: AsyncSession = Depends(get_db), current_user: int = 1):
    return await create_room(db, name=room_data.name, owner_id=current_user)


@router.get("/", response_model=List[RoomResponse])
async def get_my_rooms(db: AsyncSession = Depends(get_db), current_user: int = 1):
    rooms = await get_user_rooms(db, user_id=current_user)
    return rooms