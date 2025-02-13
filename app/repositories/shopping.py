from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.models import ShoppingItem
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate
from app.services.access_control import has_access_to_room
from app.websockets.manager import websocket_manager


async def add_item(db: AsyncSession, item_data: ShoppingItemCreate, user_id: int):
    if not await has_access_to_room(db, user_id, item_data.room_id):
        return {"error": "Access denied."}

    item = ShoppingItem(**item_data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)

    message = (
        f"🛍 *Новий товар додано!* ✅\n"
        f"📌 Назва: *{item.name}*\n"
        f"🗂 Категорія: `{item.category if item.category else 'Без категорії'}`\n"
        f"👤 Додав: _User {user_id}_"
    )
    await websocket_manager.send_message(item_data.room_id, message)

    return item


async def get_items(db: AsyncSession, room_id: int, user_id: int):
    if not await has_access_to_room(db, user_id, room_id):
        return {"error": "Access denied."}

    result = await db.execute(select(ShoppingItem).where(ShoppingItem.room_id == room_id))
    return result.scalars().all()


async def update_item(db: AsyncSession, item_id: int, item_data: ShoppingItemUpdate, user_id: int):
    item = await db.get(ShoppingItem, item_id)

    if item and await has_access_to_room(db, user_id, item.room_id):
        old_name = item.name
        old_category = item.category

        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        await db.commit()
        await db.refresh(item)

        message = (
            f"🔄 *Товар оновлено!* ✏️\n"
            f"📌 Назва: *{old_name}* ➝ *{item.name}*\n"
            f"🗂 Категорія: `{old_category if old_category else 'Без категорії'}` ➝ `{item.category if item.category else 'Без категорії'}`\n"
            f"👤 Оновив: _User {user_id}_"
        )

        await websocket_manager.send_message(item.room_id, message)

        return item

    return {"error": "Access denied."}


async def delete_item(db: AsyncSession, item_id: int, user_id: int):
    item = await db.get(ShoppingItem, item_id)
    if item and await has_access_to_room(db, user_id, item.room_id):
        await db.delete(item)
        await db.commit()

        message = (
            f"🚨 *Товар видалено!* ❌\n"
            f"📌 Назва: *{item.name}*\n"
            f"👤 Видалив: _User {user_id}_"
        )
        await websocket_manager.send_message(item.room_id, message)

        return {"message": "Item successfully deleted."}

    return {"error": "Access denied."}
