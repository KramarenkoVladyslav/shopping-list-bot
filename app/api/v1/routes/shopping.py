from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.shopping import add_item, get_items, update_item, delete_item
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse

router = APIRouter(prefix="/shopping", tags=["Shopping routes"])


@router.post("/", response_model=ShoppingItemResponse)
async def create_item(item_data: ShoppingItemCreate, db: AsyncSession = Depends(get_db), current_user: int = 1):
    result = await add_item(db, item_data, current_user)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.get("/{room_id}", response_model=List[ShoppingItemResponse])
async def read_items(room_id: int, db: AsyncSession = Depends(get_db), current_user: int = 1):
    result = await get_items(db, room_id, current_user)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.put("/{item_id}", response_model=ShoppingItemResponse)
async def modify_item(item_id: int, item_data: ShoppingItemUpdate, db: AsyncSession = Depends(get_db),
                      current_user: int = 1):
    result = await update_item(db, item_id, item_data, current_user)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.delete("/{item_id}")
async def remove_item(item_id: int, db: AsyncSession = Depends(get_db), current_user: int = 1):
    result = await delete_item(db, item_id, current_user)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result
