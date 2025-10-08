from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class OCRJobStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class OCRJob(Base):
    __tablename__ = 'ocr_jobs'

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(2048), nullable=False)  # Increased length for potential long URLs
    raw_ocr_output = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Store structured data after parsing
    status = Column(Enum(OCRJobStatus), default=OCRJobStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<OCRJob(id={self.id}, status='{self.status}', image_url='{self.image_url[:50]}...')>"