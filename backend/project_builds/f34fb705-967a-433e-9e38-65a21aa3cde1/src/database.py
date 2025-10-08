import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# Load environment variables
# For production, DATABASE_URL must be set.
# For local development, you can set it in a .env file or directly in your environment.
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Security Fix: Remove hardcoded sensitive information ---
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please configure your database connection string.")
# --- End Security Fix ---

# Configure the SQLAlchemy engine
# Use QueuePool for better connection management in a web application context.
# pool_size: The number of connections to keep open in the pool.
# max_overflow: The number of connections that can be opened beyond the pool_size.
# pool_timeout: The number of seconds to wait before giving up on getting a connection from the pool.
# pool_recycle: The number of seconds after which a connection is closed and recreated.
#               This helps prevent issues with stale connections, especially with databases
#               that might close idle connections.
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=3600 # Recycle connections every hour
)

# Create a SessionLocal class
# Each instance of the SessionLocal class will be a database session.
# The `autocommit` is set to `False` to prevent unexpected commits.
# The `autoflush` is set to `False` so that query operations don't flush pending changes to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

# Dependency for database session
def get_db():
    """
    Provides a SQLAlchemy session to be used as a dependency.
    Ensures the session is properly closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# You might want to add a function to initialize the database (create tables)
# This is typically called once when the application starts or during migrations.
def init_db():
    """
    Initializes the database by creating all tables defined in Base.metadata.
    This should generally be used for development or testing.
    For production, consider using Alembic for database migrations.
    """
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    # Example usage (for testing connection or initial setup)
    try:
        print("Attempting to connect to the database...")
        # Try to get a session to test the connection
        with SessionLocal() as db_session:
            # Perform a simple query to ensure connection is live
            db_session.execute("SELECT 1")
        print("Database connection successful!")
        # Uncomment the line below if you want to create tables when running this file directly
        # init_db()
        # print("Database tables initialized (if models were defined).")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error connecting to or initializing the database: {e}")