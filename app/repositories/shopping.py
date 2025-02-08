from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.models import ShoppingItem
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate
from app.services.access_control import has_access_to_room


# Add a new shopping item with validation and access check
async def add_item(db: AsyncSession, item_data: ShoppingItemCreate, user_id: int):
    if not await has_access_to_room(db, user_id, item_data.room_id):
        return {"error": "Access denied to this room"}

    item = ShoppingItem(**item_data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


# Get all items for a specific room with access check
async def get_items(db: AsyncSession, room_id: int, user_id: int):
    if not await has_access_to_room(db, user_id, room_id):
        return {"error": "Access denied to this room"}

    result = await db.execute(select(ShoppingItem).where(ShoppingItem.room_id == room_id))
    return result.scalars().all()


# Update a shopping item with validation and access check
async def update_item(db: AsyncSession, item_id: int, item_data: ShoppingItemUpdate, user_id: int):
    item = await db.get(ShoppingItem, item_id)
    if item and await has_access_to_room(db, user_id, item.room_id):
        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return item
    return {"error": "Access denied to this item"}


# Delete a shopping item with access check
async def delete_item(db: AsyncSession, item_id: int, user_id: int):
    item = await db.get(ShoppingItem, item_id)
    if item and await has_access_to_room(db, user_id, item.room_id):
        await db.delete(item)
        await db.commit()
        return {"message": "Item deleted successfully"}
    return {"error": "Access denied to this item"}
