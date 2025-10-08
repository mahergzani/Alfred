from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import NonNegativeFloat, PositiveInt


# --- Exercise Schemas ---
class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ExerciseCreate(ExerciseBase):
    """Schema for creating a new exercise."""
    pass


class ExerciseResponse(ExerciseBase):
    """Schema for responding with exercise details."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Workout Exercise Schemas (how an exercise is used within a workout) ---
class WorkoutExerciseBase(BaseModel):
    sets: PositiveInt = Field(..., description="Number of sets for this exercise.")
    reps: PositiveInt = Field(..., description="Number of repetitions per set.")
    weight: NonNegativeFloat = Field(..., description="Weight used for the exercise (e.g., in kg or lbs).")
    notes: Optional[str] = Field(None, max_length=500, description="Specific notes for this exercise in the workout.")


class WorkoutExerciseCreate(WorkoutExerciseBase):
    """Schema for adding an exercise to a workout during creation."""
    exercise_id: int = Field(..., description="ID of the exercise to include in the workout.")


class WorkoutExerciseResponse(WorkoutExerciseBase):
    """Schema for responding with details of an exercise within a workout."""
    id: int  # The ID of the workout_exercise entry itself
    exercise: ExerciseResponse  # Nested Exercise details

    model_config = ConfigDict(from_attributes=True)


# --- Workout Schemas ---
class WorkoutBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the workout plan.")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the workout plan.")


class WorkoutCreate(WorkoutBase):
    """Schema for creating a new workout."""
    exercises: list[WorkoutExerciseCreate] = Field(
        ...,
        min_length=1,
        description="List of exercises to include in the workout."
    )


class WorkoutUpdate(BaseModel):
    """Schema for updating an existing workout. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    # When updating, typically the entire list of exercises is replaced
    # or specific endpoints are used for adding/removing individual workout exercises.
    # For simplicity, this schema assumes full replacement of the list if provided.
    exercises: Optional[list[WorkoutExerciseCreate]] = Field(
        None,
        min_length=1,
        description="Optional list of exercises to update the workout with. Replaces existing exercises if provided."
    )


class WorkoutResponse(WorkoutBase):
    """Schema for responding with full workout details."""
    id: int
    exercises: list[WorkoutExerciseResponse] = Field(
        ...,
        description="List of exercises included in the workout, with their specific parameters."
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)