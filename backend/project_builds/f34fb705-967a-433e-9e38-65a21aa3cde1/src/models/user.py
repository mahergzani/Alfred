from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON  # For generic JSON support, use JSONB from sqlalchemy.dialects.postgresql for PostgreSQL-specific JSONB type.

Base = declarative_base()

class User(Base):
    """
    Represents a user in the system.
    Stores core user information including authentication credentials and personal details.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # hashed_password column length increased to 512 characters as per security best practices.
    # This accommodates longer hashes from modern, robust algorithms like Argon2id or bcrypt.
    # It is crucial that the application layer stores only securely hashed passwords (e.g., using bcrypt, Argon2id, scrypt).
    # Never store plain passwords or use insecure hashing algorithms.
    hashed_password = Column(String(512), nullable=False)
    personal_details = Column(JSON, nullable=True, default={})  # Stores flexible personal data in JSON format.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"