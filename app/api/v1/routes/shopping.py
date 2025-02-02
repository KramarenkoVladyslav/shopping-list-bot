from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.shopping import get_items, get_item, create_item, update_item, delete_item
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse

router = APIRouter(prefix="/shopping", tags=["Shopping routes"])


@router.get("/", response_model=List[ShoppingItemResponse])
async def list_items(db: AsyncSession = Depends(get_db)):
    return await get_items(db)


@router.get("/{item_id}", response_model=ShoppingItemResponse)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ShoppingItemResponse)
async def create_new_item(item_data: ShoppingItemCreate, db: AsyncSession = Depends(get_db)):
    return await create_item(db, item_data)


@router.put("/{item_id}", response_model=ShoppingItemResponse)
async def update_item(item_id, item_data: ShoppingItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await update_item(db, item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", response_model=ShoppingItemResponse)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await delete_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item