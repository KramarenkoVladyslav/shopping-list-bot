import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Room, RoomUser


# Function to create room
async def create_room(db: AsyncSession, name: str, owner_id: int):
    invite_code = str(uuid.uuid4())[:8]
    room = Room(name=name, owner_id=owner_id, invite_code=invite_code)
    db.add(room)
    await db.commit()
    await db.refresh(room)

    room_user = RoomUser(room_id=room.id, user_id=owner_id)
    db.add(room_user)
    await db.commit()

    return room


# Function to retrieve all rooms for a specific user
async def get_user_rooms(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Room).join(RoomUser).where(RoomUser.user_id == user_id)
    )

    return result.scalars().all()


# Function to update the room name
async def update_room(db: AsyncSession, room_id: int, new_name: str, user_id: int):
    room = await db.get(Room, room_id)
    if room and room.owner_id == user_id:
        room.name = new_name
        await db.commit()
        await db.refresh(room)
        return room
    return None


# Function to update the room name
async def delete_room(db: AsyncSession, room_id: int, user_id: int):
    room = await db.get(Room, room_id)
    if room and room.owner_id == user_id:
        await db.delete(room)
        await db.commit()
        return {'message': 'Room deleted successfully'}
    return {"error": "You are not authorized to delete this room"}