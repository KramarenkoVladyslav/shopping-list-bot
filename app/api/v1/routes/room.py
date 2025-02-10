from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User
from app.repositories.room import create_room, get_user_rooms, update_room, join_room
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["Room routes"])


@router.post("/", response_model=RoomResponse)
async def create_new_room(room_data: RoomCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_room(db, name=room_data.name, owner_id=current_user.id)


@router.get("/", response_model=List[RoomResponse])
async def get_my_rooms(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rooms = await get_user_rooms(db, user_id=current_user.id)
    return rooms


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(room_id: int, room_data: RoomUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = await update_room(db, room_id=room_id, new_name=room_data.name, user_id=current_user.id)
    if not room:
        raise HTTPException(status_code=403, detail="You are not authorized to update this room")
    return room


@router.delete("/{room_id}", response_model=RoomResponse)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await delete_room(db, room_id=room_id, user_id=current_user.id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.post("/join/{invite_code}")
async def join_room_endpoint(invite_code: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await join_room(db, invite_code, current_user.id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result
