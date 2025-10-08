import os
from datetime import timedelta

class Config:
    # General App Config
    # SECRET_KEY is crucial for security. It should be a strong, random value set via environment variable.
    # In production, this MUST be set.
    SECRET_KEY = os.getenv('SECRET_KEY')
    APP_NAME = os.getenv('APP_NAME', 'Image_Processor')
    DEBUG = False

    # Database Config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Config
    JWT_TOKEN_LOCATION = ['headers']
    # JWT_SECRET_KEY inherits from SECRET_KEY. This ensures consistency and simplifies key management.
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # OCR API Config
    # These credentials should be securely managed, ideally through environment variables or a secrets manager.
    OCR_API_KEY = os.getenv('OCR_API_KEY')
    OCR_API_BASE_URL = os.getenv('OCR_API_BASE_URL', 'https://api.ocr.space/parse/image')

    # Rate Limit Config
    # Configure storage for rate limits (e.g., Redis for production). Default to in-memory for simplicity.
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    # Default rate limit for all endpoints if not specified otherwise.
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '20 per minute')
    # Rate limit strategy (e.g., 'fixed-window', 'moving-window').
    RATELIMIT_STRATEGY = os.getenv('RATELIMIT_STRATEGY', 'fixed-window')

    # Security Headers (Uncomment and configure as needed for production)
    # SECURITY_HEADERS = {
    #     "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self';",
    #     "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    #     "X-Content-Type-Options": "nosniff",
    #     "X-Frame-Options": "SAMEORIGIN",
    #     "X-XSS-Protection": "1; mode=block",
    # }
    # Note: 'unsafe-inline' in CSP should be avoided. If used, ensure it's absolutely necessary and understand the risks.
    # Prioritize using hashes or nonces for scripts/styles.

class DevelopmentConfig(Config):
    DEBUG = True
    # Provide a clear, non-production-threatening default for development.
    # Still allows overriding via environment variable.
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_please_change_this_for_prod')
    JWT_SECRET_KEY = SECRET_KEY # Use the dev-specific secret key
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    # OCR API Key and URL can remain None or point to mock services for dev if not needed for local testing.

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # Use in-memory SQLite for tests for speed and isolation
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # A distinct secret key for testing, explicitly set to avoid environment dependency
    SECRET_KEY = 'test_secret_key'
    JWT_SECRET_KEY = SECRET_KEY
    # Mock OCR API during tests or use a dummy key
    OCR_API_KEY = 'test_ocr_key'
    OCR_API_BASE_URL = 'http://mock-ocr-api.test'
    RATELIMIT_STORAGE_URL = 'memory://' # Ensure rate limits don't interfere with tests

class ProductionConfig(Config):
    DEBUG = False
    # Critical security validation: Ensure sensitive configuration variables are set in production.
    # If not set, raise an error to prevent insecure defaults or missing configurations.
    if not Config.SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable not set for production.")
    if not Config.OCR_API_KEY:
        raise ValueError("OCR_API_KEY environment variable not set for production.")
    if not Config.OCR_API_BASE_URL:
        raise ValueError("OCR_API_BASE_URL environment variable not set for production.")

    # Override defaults with potentially stronger production settings if needed
    # Example: Shorter JWT lifespan, stricter rate limits
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '10 per minute')

# Mapping for convenience to load configuration based on environment
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # Fallback if FLASK_ENV is not set
}