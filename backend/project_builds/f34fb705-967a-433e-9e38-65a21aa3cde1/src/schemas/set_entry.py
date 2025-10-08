from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class SetEntryBase(BaseModel):
    """Base schema for common SetEntry fields."""
    set_id: UUID = Field(..., description="The ID of the set this entry belongs to.")
    term: str = Field(..., min_length=1, max_length=255, description="The term or question for the entry.")
    definition: str = Field(..., min_length=1, description="The definition or answer for the entry.")
    notes: Optional[str] = Field(None, max_length=1024, description="Additional notes or context for the entry.")
    image_url: Optional[HttpUrl] = Field(None, description="An optional URL for an image related to the entry.")
    position: Optional[int] = Field(None, ge=0, description="The optional position of the entry within the set for ordering.")


class SetEntryCreate(SetEntryBase):
    """Schema for creating a new SetEntry."""
    # All fields from SetEntryBase are required by default for creation,
    # but optional fields can still be omitted.
    pass


class SetEntryUpdate(BaseModel):
    """Schema for updating an existing SetEntry."""
    # All fields are optional for partial updates
    set_id: Optional[UUID] = Field(None, description="The ID of the set this entry belongs to.")
    term: Optional[str] = Field(None, min_length=1, max_length=255, description="The term or question for the entry.")
    definition: Optional[str] = Field(None, min_length=1, description="The definition or answer for the entry.")
    notes: Optional[str] = Field(None, max_length=1024, description="Additional notes or context for the entry.")
    image_url: Optional[HttpUrl] = Field(None, description="An optional URL for an image related to the entry.")
    position: Optional[int] = Field(None, ge=0, description="The optional position of the entry within the set for ordering.")


class SetEntryResponse(SetEntryBase):
    """Schema for returning a SetEntry."""
    id: UUID = Field(..., description="The unique identifier of the set entry.")
    created_at: datetime = Field(..., description="Timestamp when the set entry was created.")
    updated_at: datetime = Field(..., description="Timestamp when the set entry was last updated.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "set_id": "8a2f3b9c-c0d1-4e5a-8b2f-3c1d0e9a7f65",
                "term": "Python",
                "definition": "An interpreted, object-oriented, high-level programming language with dynamic semantics.",
                "notes": "Often used for web development, data science, AI, and automation.",
                "image_url": "https://example.com/python_logo.png",
                "position": 1,
                "created_at": "2023-01-15T10:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }