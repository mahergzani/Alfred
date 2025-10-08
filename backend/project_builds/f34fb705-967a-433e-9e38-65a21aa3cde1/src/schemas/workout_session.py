from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- SetEntry Schemas ---

class SetEntryBase(BaseModel):
    exercise_id: UUID = Field(..., description="ID of the exercise performed in this set.")
    set_number: int = Field(..., gt=0, description="The sequential number of the set within the exercise.")
    reps: int = Field(..., ge=0, description="Number of repetitions performed in the set.")
    weight: float = Field(..., ge=0, description="Weight used for the set in kilograms (or other specified unit).")
    notes: Optional[str] = Field(None, max_length=500, description="Any specific notes for this set.")
    is_warmup: bool = Field(False, description="Indicates if this set was a warm-up set.")


class SetEntryCreate(SetEntryBase):
    """Schema for creating a new SetEntry."""
    # Inherits all fields from SetEntryBase.
    # No additional fields for creation beyond the base.
    pass


class SetEntryResponse(SetEntryBase):
    """Schema for returning a SetEntry."""
    id: UUID = Field(..., description="Unique identifier of the set entry.")
    workout_session_id: UUID = Field(..., description="ID of the workout session this set belongs to.")

    class Config:
        from_attributes = True  # Enable ORM mode for Pydantic v2 to allow mapping from ORM objects


# --- WorkoutSession Schemas ---

class WorkoutSessionBase(BaseModel):
    user_id: UUID = Field(..., description="ID of the user who performed the workout session.")
    start_time: datetime = Field(..., description="The date and time the workout session started.")
    end_time: Optional[datetime] = Field(None, description="The date and time the workout session ended. Can be null if ongoing.")
    notes: Optional[str] = Field(None, max_length=1000, description="General notes for the workout session.")


class WorkoutSessionCreate(WorkoutSessionBase):
    """Schema for creating a new WorkoutSession."""
    sets: Optional[List[SetEntryCreate]] = Field([], description="Initial list of set entries for the workout session.")


class WorkoutSessionUpdate(WorkoutSessionBase):
    """Schema for updating an existing WorkoutSession."""
    # All fields are optional for updates as only partial data might be sent.
    user_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    # Sets are typically managed via dedicated sub-endpoints to avoid complex patch logic for nested lists.


class WorkoutSessionResponse(WorkoutSessionBase):
    """Schema for returning a WorkoutSession."""
    id: UUID = Field(..., description="Unique identifier of the workout session.")
    sets: List[SetEntryResponse] = Field([], description="List of all set entries performed in this workout session.")
    # Duration can be calculated on the fly or stored. Including it here suggests it might be computed for the response.
    duration_minutes: Optional[int] = Field(None, description="Calculated duration of the workout session in minutes.")

    class Config:
        from_attributes = True  # Enable ORM mode for Pydantic v2 to allow mapping from ORM objects