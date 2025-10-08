from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class MealEntryNutritionalData(BaseModel):
    """
    Schema for detailed nutritional data of a food item.
    Defaults to 0.0 for all fields, assuming that if a value is not
    explicitly provided or parsed, its quantity is zero.
    """
    calories: float = Field(default=0.0, ge=0.0, description="Total calories (kcal)")
    protein_g: float = Field(default=0.0, ge=0.0, description="Protein content (grams)")
    carbohydrates_g: float = Field(default=0.0, ge=0.0, description="Total carbohydrate content (grams)")
    fat_g: float = Field(default=0.0, ge=0.0, description="Total fat content (grams)")
    fiber_g: float = Field(default=0.0, ge=0.0, description="Fiber content (grams)")
    sugar_g: float = Field(default=0.0, ge=0.0, description="Sugar content (grams)")
    sodium_mg: float = Field(default=0.0, ge=0.0, description="Sodium content (milligrams)")
    cholesterol_mg: float = Field(default=0.0, ge=0.0, description="Cholesterol content (milligrams)")
    saturated_fat_g: float = Field(default=0.0, ge=0.0, description="Saturated fat content (grams)")
    trans_fat_g: float = Field(default=0.0, ge=0.0, description="Trans fat content (grams)")

class MealEntryBase(BaseModel):
    """
    Base schema for common MealEntry fields, used for creation.
    """
    user_id: UUID = Field(description="The ID of the user who logged the meal entry.")
    meal_time: datetime = Field(description="The timestamp when the meal was consumed.")
    food_item_name: str = Field(min_length=1, max_length=255, description="The name of the food item.")
    quantity: float = Field(gt=0.0, description="The quantity of the food item consumed. Must be greater than 0.")
    unit: str = Field(min_length=1, max_length=50, description="The unit of measurement for the quantity (e.g., 'g', 'ml', 'cup', 'serving').")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Optional notes about the meal entry.")

class MealEntryCreate(MealEntryBase):
    """
    Schema for creating a new MealEntry.
    Inherits all fields from MealEntryBase.
    """
    pass

class MealEntryUpdate(BaseModel):
    """
    Schema for updating an existing MealEntry. All fields are optional.
    The user_id is typically immutable and not updated via this schema.
    """
    meal_time: Optional[datetime] = Field(default=None, description="The timestamp when the meal was consumed.")
    food_item_name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="The name of the food item.")
    quantity: Optional[float] = Field(default=None, gt=0.0, description="The quantity of the food item consumed. Must be greater than 0 if provided.")
    unit: Optional[str] = Field(default=None, min_length=1, max_length=50, description="The unit of measurement for the quantity.")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Optional notes about the meal entry.")

class MealEntryResponse(MealEntryBase):
    """
    Schema for a MealEntry response, including its unique ID, timestamps,
    and the associated parsed nutritional data.
    """
    id: UUID = Field(description="The unique identifier of the meal entry.")
    nutritional_data: MealEntryNutritionalData = Field(description="Parsed nutritional data for the food item.")
    created_at: datetime = Field(description="Timestamp when the meal entry was created.")
    updated_at: datetime = Field(description="Timestamp when the meal entry was last updated.")

    class Config:
        from_attributes = True # Enable Pydantic to read data from ORM models (e.g., SQLAlchemy)