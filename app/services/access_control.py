from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import RoomUser


# Function to check if a user has access to a specific room
async def has_access_to_room(db: AsyncSession, user_id: int, room_id: int) -> bool:
    result = await db.execute(
        select(RoomUser).where(RoomUser.room_id == room_id).where(RoomUser.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None
