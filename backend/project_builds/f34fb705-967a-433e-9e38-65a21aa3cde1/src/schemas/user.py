from pydantic import BaseModel, Field, EmailStr

# Minimum password length for security
MIN_PASSWORD_LENGTH = 8

class UserRegister(BaseModel):
    """
    Pydantic schema for user registration requests.
    Requires an email and a password.
    """
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        example="StrongPassword123!",
        description=f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
    )

class UserLogin(BaseModel):
    """
    Pydantic schema for user login requests.
    Requires an email and a password.
    """
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="StrongPassword123!")

class UserProfile(BaseModel):
    """
    Pydantic schema for user profile responses.
    Excludes sensitive information like password hashes.
    """
    id: int = Field(..., example=1, description="Unique identifier of the user.")
    email: EmailStr = Field(..., example="user@example.com", description="Email address of the user.")

    class Config:
        from_attributes = True # Allows creation from ORM models