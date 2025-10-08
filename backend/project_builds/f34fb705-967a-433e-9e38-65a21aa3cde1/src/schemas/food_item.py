from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, HttpUrl

# Base schema for common fields
class FoodItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the food item")
    description: Optional[str] = Field(None, max_length=500, description="Description of the food item")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Price of the food item, must be greater than 0")
    category: Optional[str] = Field(None, max_length=50, description="Category of the food item")
    image_url: Optional[HttpUrl] = Field(None, description="URL of the food item's image")
    is_available: bool = Field(True, description="Availability status of the food item")

# Schema for creating a new food item
class FoodItemCreate(FoodItemBase):
    pass

# Schema for updating an existing food item
# All fields are optional as updates might only touch specific fields
class FoodItemUpdate(FoodItemBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the food item")
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Price of the food item, must be greater than 0")
    is_available: Optional[bool] = Field(None, description="Availability status of the food item")

# Schema for the response model (what is returned after creation/fetch)
class FoodItemResponse(FoodItemBase):
    id: int = Field(..., gt=0, description="Unique identifier of the food item")

    class Config:
        from_attributes = True  # Enable ORM mode for Pydantic v2
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Spicy Chicken Burger",
                "description": "A delicious burger with spicy chicken patty, lettuce, tomato, and special sauce.",
                "price": 12.99,
                "category": "Burgers",
                "image_url": "https://example.com/images/spicy_chicken_burger.jpg",
                "is_available": True
            }
        }