import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Union

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# --- JWT Configuration ---
# Critical: Insecure Default JWT_SECRET_KEY Handling
# Ensure the SECRET_KEY is loaded from environment variables and is not using an insecure default.
# Raise a ValueError if the key is not set or is insecure to prevent the application from starting.
INSECURE_DEFAULT_KEY = "your-super-secret-key-that-should-be-very-long-and-random"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY or SECRET_KEY == INSECURE_DEFAULT_KEY:
    error_msg = (
        "CRITICAL: JWT_SECRET_KEY environment variable is not set or is using an insecure default value. "
        "This must be a long, random, and unguessable string. "
        "DO NOT USE IN PRODUCTION without setting a proper, unique key!"
    )
    logger.critical(error_msg)
    raise ValueError(error_msg)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Default expiration for access tokens

# --- Password Hashing Functions ---

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    Args:
        password: The plain-text password to hash.

    Returns:
        The hashed password as a string.
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    if not password:
        raise ValueError("Password cannot be empty.")

    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a bcrypt-hashed password.

    Args:
        plain_password: The plain-text password to verify.
        hashed_password: The bcrypt-hashed password from storage.

    Returns:
        True if the password matches, False otherwise.
    """
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        raise TypeError("Both plain_password and hashed_password must be strings.")
    if not plain_password or not hashed_password:
        return False # Can't verify empty strings

    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError as e:
        logger.error(f"Error during password verification: {e}")
        return False

# --- JWT Token Functions ---

def create_jwt_token(data: Dict[str, Union[str, int]], expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT token with the given data and optional expiration delta.

    Args:
        data: A dictionary containing the payload for the token.
        expires_delta: An optional timedelta object specifying the token's
                       expiration time from now. If None, a default
                       expiration of ACCESS_TOKEN_EXPIRE_MINUTES is used.

    Returns:
        The encoded JWT token as a string.
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)

    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat": now_utc.timestamp(), "exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str) -> Dict[str, Union[str, int]] | None:
    """
    Decodes and validates a JWT token.

    Args:
        token: The JWT token string to decode.

    Returns:
        The decoded payload as a dictionary if valid, None otherwise.
    """
    if not isinstance(token, str):
        logger.warning("Attempted to decode a non-string token.")
        return None
    if not token:
        logger.warning("Attempted to decode an empty token string.")
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during JWT token decoding: {e}")
        return None