from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ScheduleEntryBase(BaseModel):
    """Base schema for common schedule entry attributes, including user_id.
    This model is suitable for internal representation or ORM models where `user_id` is part of the data.
    """
    user_id: UUID = Field(..., description="The ID of the user who owns this schedule entry.")
    start_time: datetime = Field(..., description="The start date and time of the schedule entry (UTC).")
    end_time: datetime = Field(..., description="The end date and time of the schedule entry (UTC).")
    title: str = Field(..., min_length=1, max_length=255, description="A concise title for the schedule entry.")
    description: Optional[str] = Field(None, max_length=1000, description="An optional detailed description of the entry.")
    location: Optional[str] = Field(None, max_length=255, description="The optional location of the event.")
    is_private: bool = Field(False, description="Indicates if the schedule entry is private (not visible to others).")


class ScheduleEntryCreateRequest(BaseModel):
    """Schema for creating a new schedule entry, provided by the client.
    'user_id' is explicitly excluded as it will be set by the server based on the authenticated user,
    preventing mass assignment vulnerabilities.
    """
    start_time: datetime = Field(..., description="The start date and time of the schedule entry (UTC).")
    end_time: datetime = Field(..., description="The end date and time of the schedule entry (UTC).")
    title: str = Field(..., min_length=1, max_length=255, description="A concise title for the schedule entry.")
    description: Optional[str] = Field(None, max_length=1000, description="An optional detailed description of the entry.")
    location: Optional[str] = Field(None, max_length=255, description="The optional location of the event.")
    is_private: bool = Field(False, description="Indicates if the schedule entry is private (not visible to others).")

    @model_validator(mode="after")
    def validate_times(self) -> 'ScheduleEntryCreateRequest':
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "start_time": "2023-10-27T09:00:00Z",
                "end_time": "2023-10-27T10:00:00Z",
                "title": "Daily Standup Meeting",
                "description": "Discuss progress, blockers, and plans for the day.",
                "location": "Virtual Call",
                "is_private": False,
            }
        }
    }


class ScheduleEntryUpdateRequest(BaseModel):
    """Schema for updating an existing schedule entry, provided by the client.
    All fields are optional, and 'user_id' cannot be updated by the client.
    """
    start_time: Optional[datetime] = Field(None, description="The start date and time of the schedule entry (UTC).")
    end_time: Optional[datetime] = Field(None, description="The end date and time of the schedule entry (UTC).")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="A concise title for the schedule entry.")
    description: Optional[str] = Field(None, max_length=1000, description="An optional detailed description of the entry.")
    location: Optional[str] = Field(None, max_length=255, description="The optional location of the event.")
    is_private: Optional[bool] = Field(None, description="Indicates if the schedule entry is private (not visible to others).")

    @model_validator(mode="after")
    def validate_times(self) -> 'ScheduleEntryUpdateRequest':
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Updated Daily Standup",
                "location": "Zoom Call",
                "is_private": True,
            }
        }
    }


class ScheduleEntryResponse(ScheduleEntryBase):
    """Schema for a schedule entry response, including server-generated fields."""
    id: UUID = Field(..., description="The unique ID of the schedule entry.")
    created_at: datetime = Field(..., description="The timestamp when the schedule entry was created (UTC).")
    updated_at: datetime = Field(..., description="The timestamp when the schedule entry was last updated (UTC).")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "user_id": "00000000-0000-0000-0000-000000000001",
                "start_time": "2023-10-27T09:00:00Z",
                "end_time": "2023-10-27T10:00:00Z",
                "title": "Daily Standup Meeting",
                "description": "Discuss progress, blockers, and plans for the day.",
                "location": "Virtual Call",
                "is_private": False,
                "created_at": "2023-10-26T14:30:00Z",
                "updated_at": "2023-10-26T14:30:00Z",
            }
        }
    }