import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.models import Room, RoomUser
from app.websockets.manager import websocket_manager


async def create_room(db: AsyncSession, name: str, owner_id: int):
    invite_code = str(uuid.uuid4())[:8]
    room = Room(name=name, owner_id=owner_id, invite_code=invite_code)
    db.add(room)
    await db.commit()
    await db.refresh(room)

    room_user = RoomUser(room_id=room.id, user_id=owner_id)
    db.add(room_user)
    await db.commit()

    message = (
        f"📢 *Нова кімната створена!* 🏠\n"
        f"👤 Власник: _User {owner_id}_\n"
        f"🛒 Назва кімнати: *{room.name}*\n"
        f"🔑 Код запрошення: `{room.invite_code}`"
    )
    await websocket_manager.send_message(room.id, message)

    return room


async def get_user_rooms(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Room).join(RoomUser).where(RoomUser.user_id == user_id)
    )
    return result.scalars().all()


async def update_room(db: AsyncSession, room_id: int, new_name: str, user_id: int):
    room = await db.get(Room, room_id)
    if room and room.owner_id == user_id:
        old_name = room.name
        room.name = new_name
        await db.commit()
        await db.refresh(room)

        message = (
            f"🔄 *Назва кімнати оновлена!* ✏️\n"
            f"🛒 {old_name} ➝ *{room.name}*\n"
            f"👤 Оновив: _User {user_id}_"
        )
        await websocket_manager.send_message(room.id, message)

        return room

    raise HTTPException(status_code=403, detail="Access denied.")


async def delete_room(db: AsyncSession, room_id: int, user_id: int):
    room = await db.get(Room, room_id)
    if room and room.owner_id == user_id:
        await db.delete(room)
        await db.commit()

        message = (
            f"❌ *Кімнату видалено!* 🏠\n"
            f"🛒 Назва: *{room.name}*\n"
            f"👤 Видалив: _User {user_id}_"
        )
        await websocket_manager.send_message(room.id, message)

        return {"message": "Room successfully deleted."}

    raise HTTPException(status_code=403, detail="Access denied.")


async def join_room(db: AsyncSession, invite_code: str, user_id: int):
    result = await db.execute(select(Room).where(Room.invite_code == invite_code))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    user_check = await db.execute(
        select(RoomUser).where(RoomUser.room_id == room.id, RoomUser.user_id == user_id)
    )
    existing_member = user_check.scalar_one_or_none()
    if existing_member:
        raise HTTPException(status_code=409, detail="You are already a member of this room.")

    new_member = RoomUser(room_id=room.id, user_id=user_id)
    db.add(new_member)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")
    await db.refresh(new_member)

    message = (
        f"✅ *Новий учасник у кімнаті!* 🎉\n"
        f"🛒 Кімната: *{room.name}*\n"
        f"👤 Приєднався: _User {user_id}_"
    )
    await websocket_manager.send_message(room.id, message)

    return {"name": room.name, "message": "Successfully joined the room"}