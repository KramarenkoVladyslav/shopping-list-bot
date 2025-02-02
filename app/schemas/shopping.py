from typing import Optional

from pydantic import BaseModel


# Base schema for a shopping item
class ShoppingItemBase(BaseModel):
    name: str
    category: Optional[str] = None


# Schema for creating a new shopping item
class ShoppingItemCreate(ShoppingItemBase):
    pass


# Schema for updating an existing shopping item
class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


# Schema for API response
class ShoppingItemResponse(ShoppingItemBase):
    id: int  # Unique identifier for the item

    class Config:
        from_attributes = True