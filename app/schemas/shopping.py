from typing import Optional

from pydantic import BaseModel, Field


# Schema for creating a new shopping item
class ShoppingItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the item")
    category: Optional[str] = Field(None, min_length=1, max_length=50, description="Category of the item (optional)")
    room_id: int = Field(..., gt=0, description="ID of the room where the item will be added")


# Schema for updating an existing shopping item
class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated name of the item")
    category: Optional[str] = Field(None, min_length=1, max_length=50, description="Updated category of the item")


# Schema for API response
class ShoppingItemResponse(BaseModel):
    id: int  # Unique identifier for the item
    name: str
    category: Optional[str] = None
    room_id: int

    class Config:
        from_attributes = True


