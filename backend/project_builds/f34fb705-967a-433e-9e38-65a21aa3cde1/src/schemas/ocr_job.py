from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, HttpUrl, Field

# Define an Enum for OCR Job status
class OCRJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Request model for creating an OCR Job
class OCRJobRequest(BaseModel):
    image_url: HttpUrl = Field(
        ...,
        title="Image URL",
        description="The URL of the image to be processed by OCR.",
        examples=["https://example.com/invoice.png"]
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        title="OCR Configuration",
        description="Optional configuration parameters for the OCR engine (e.g., language, specific models, output format).",
        examples=[{"language": "en", "output_format": "hocr"}]
    )

# Response model for an OCR Job
class OCRJobResponse(BaseModel):
    job_id: UUID = Field(
        ...,
        title="Job ID",
        description="Unique identifier for the OCR job.",
        examples=[uuid4()]
    )
    status: OCRJobStatus = Field(
        ...,
        title="Job Status",
        description="The current status of the OCR job.",
        examples=[OCRJobStatus.PENDING]
    )
    image_url: HttpUrl = Field(
        ...,
        title="Image URL",
        description="The URL of the image that was processed.",
        examples=["https://example.com/invoice.png"]
    )
    parsed_data: Optional[Dict[str, Any]] = Field(
        None,
        title="Parsed Data",
        description="The structured data extracted from the image by the OCR engine. This field is populated only if status is COMPLETED.",
        examples=[{"invoice_number": "INV-2023-001", "total_amount": "123.45", "line_items": [{"description": "Item A", "quantity": 1, "price": 100.00}]}]
    )
    error_message: Optional[str] = Field(
        None,
        title="Error Message",
        description="Details about the error if the job failed.",
        examples=["Image not accessible or invalid format."]
    )
    created_at: datetime = Field(
        ...,
        title="Creation Timestamp",
        description="Timestamp when the OCR job was created.",
        examples=[datetime.now()]
    )
    updated_at: datetime = Field(
        ...,
        title="Last Update Timestamp",
        description="Timestamp when the OCR job was last updated.",
        examples=[datetime.now()]
    )

    class Config:
        # Pydantic v2 automatically handles UUID and datetime serialization.
        # For older Pydantic versions or explicit control:
        # json_encoders = {
        #     UUID: str,
        #     datetime: lambda dt: dt.isoformat(),
        # }
        # This setting is more for documentation generation in FastAPI with older Pydantic
        # or for allowing specific types that Pydantic might otherwise complain about during schema definition.
        # For actual runtime, Pydantic's default encoders are usually sufficient.
        # We can remove `arbitrary_types_allowed` if not strictly needed, relying on Pydantic's strong typing.
        pass