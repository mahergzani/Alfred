from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

# Base schema for common exercise attributes.
# All fields are defined as Optional here to facilitate reusability for updates,
# where all fields are typically optional for partial updates.
class ExerciseBase(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Name of the exercise")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the exercise")
    category: Optional[str] = Field(None, max_length=50, description="Category of the exercise (e.g., Strength, Cardio, Flexibility)")
    muscle_group: Optional[str] = Field(None, max_length=50, description="Primary muscle group targeted (e.g., Chest, Back, Legs)")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="Difficulty level of the exercise (1-5)")
    equipment: Optional[str] = Field(None, max_length=100, description="Equipment required for the exercise")

# Schema for creating a new exercise.
# 'name' is explicitly made required for creation, overriding the Optional from ExerciseBase.
# Other fields remain optional as defined in ExerciseBase.
class ExerciseCreate(ExerciseBase):
    name: str = Field(..., min_length=3, max_length=100, description="Name of the exercise")

# Schema for updating an existing exercise.
# All fields inherit their Optional status from ExerciseBase, allowing for partial updates.
class ExerciseUpdate(ExerciseBase):
    pass

# Schema for the exercise response model.
# This includes the unique identifier 'id' and makes 'name' required,
# assuming a successfully created exercise will always have a name.
class ExerciseResponse(ExerciseBase):
    id: UUID = Field(..., description="Unique identifier of the exercise")
    name: str = Field(..., min_length=3, max_length=100, description="Name of the exercise") # Override to make name required in response

    # Pydantic model configuration.
    # `from_attributes = True` (formerly `orm_mode = True` in Pydantic v1)
    # allows Pydantic to read data from ORM models (e.g., SQLAlchemy instances)
    # by attribute name, not just by dictionary keys.
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "name": "Push-up",
                "description": "A classic bodyweight exercise that works the chest, shoulders, and triceps.",
                "category": "Strength",
                "muscle_group": "Chest",
                "difficulty": 2,
                "equipment": "None",
            }
        }
    }