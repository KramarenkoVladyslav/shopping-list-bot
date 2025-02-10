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


# Function to join a room using an invitation code
async def join_room(db: AsyncSession, invite_code: str, user_id: int):
    # Find the room by the invite code
    result = await db.execute(select(Room).where(Room.invite_code == invite_code))
    room = result.scalar_one_or_none()

    if not room:
        return {"error": "Room not found with this invite code."}

    user_check = await db.execute(
        select(RoomUser).where(RoomUser.room_id == room.id, RoomUser.user_id == user_id)
    )
    existing_member = user_check.scalar_one_or_none()

    if existing_member:
        return {"message": "You are already a member of this room."}

    new_member = RoomUser(room_id=room.id, user_id=user_id)
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)

    return {"message": f"Successfully joined the room: {room.name}"}