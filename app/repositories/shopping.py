from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.models import ShoppingItem
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate


# Function to retrieve all shopping items from the database
async def get_items(db: AsyncSession):
    result = await db.execute(select(ShoppingItem))
    return result.scalars().all()


# Function to retrieve a single shopping item by its ID
async def get_item(db: AsyncSession, item_id: int):
    return await db.get(ShoppingItem, item_id)


# Function to create a new shopping item in the database
async def create_item(db: AsyncSession, item_data: ShoppingItemCreate):
    item = ShoppingItem(**item_data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


# Function to update an existing shopping item
async def update_item(db: AsyncSession, item_id: int, item_data: ShoppingItemUpdate):
    item = await db.get(ShoppingItem, item_id)  # Retrieves the item by ID
    if item:
        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
    return item


# Function to delete a shopping item by its ID
async def delete_item(db: AsyncSession, item_id: int):
    item = await db.get(ShoppingItem, item_id)
    if item:
        await db.delete(item)
        await db.commit()
    return item