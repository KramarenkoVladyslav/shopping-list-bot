from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.room import create_room, get_user_rooms, update_room
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["Room routes"])


@router.post("/", response_model=RoomResponse)
async def create_new_room(room_data: RoomCreate, db: AsyncSession = Depends(get_db), current_user: int = 1):
    return await create_room(db, name=room_data.name, owner_id=current_user)


@router.get("/", response_model=List[RoomResponse])
async def get_my_rooms(db: AsyncSession = Depends(get_db), current_user: int = 1):
    rooms = await get_user_rooms(db, user_id=current_user)
    return rooms


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(room_id: int, room_data: RoomUpdate, db: AsyncSession = Depends(get_db), current_user: int = 1):
    room = await update_room(db, room_id=room_id, new_name=room_data.name, user_id=current_user)
    if not room:
        raise HTTPException(status_code=403, detail="You are not authorized to update this room")
    return room


@router.delete("/{room_id}", response_model=RoomResponse)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db), current_user: int = 1):
    result = await delete_room(db, room_id=room_id, user_id=current_user)
    if 'error' in result:
        raise HTTPException(status_code=403, detail="error")
    return result