from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, RoomUser, Room


# Get all members from room
async def get_room_members(db: AsyncSession, room_id: int):
    result = await db.execute(
        select(User).join(RoomUser).where(RoomUser.room_id == room_id)
    )
    return result.scalars().all()


# Add a user to the room
async def add_user_to_room(db: AsyncSession, room_id: int, user_id: int, current_user_id: int):
    room = await db.get(Room, room_id)
    if room.owner_id != current_user_id:
        return {"error": "You are not the owner of this room."}

    existing_member = await db.execute(
        select(RoomUser).where(RoomUser.room_id == room_id, RoomUser.user_id == user_id)
    )

    if existing_member.scalar_one_or_none():
        return {"error": "User is already a member of this room."}

    new_member = RoomUser(room_id=room_id, user_id=user_id)
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return {"message": "User added successfully."}


# Remove a user from the room (only the owner can do this)
async def remove_user_from_room(db: AsyncSession, room_id: int, user_id: int, current_user_id: int):
    room = await db.get(Room, room_id)
    if room.owner_id != current_user_id:
        return {"error": "You are not the owner of this room."}

    if room.owner_id == user_id:
        return {"error": "The owner cannot be removed from the room."}

    user_to_remove = await db.execute(
        select(RoomUser).where(RoomUser.room_id == room_id, RoomUser.user_id == user_id)
    )
    member = user_to_remove.scalar_one_or_none()

    if not member:
        return {"error": "User is not a member of this room."}

    await db.delete(member)
    await db.commit()
    return {"message": "User removed successfully."}