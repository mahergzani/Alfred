from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

# Assuming 'User' and 'Workout' models are defined elsewhere and accessible
# For instance, if they are in src/models/user.py and src/models/workout.py
# and the ORM is set up to discover them, SQLAlchemy can resolve the relationships.
# We define the relationships here, and the corresponding back_populates would be
# defined in the User and Workout models respectively.

class WorkoutSession(Base):
    __tablename__ = 'workout_sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default='pending', index=True) # e.g., 'pending', 'started', 'completed', 'cancelled'

    # Define relationships with User and Workout models
    # Assuming the User model has a 'workout_sessions' back_populates relationship
    user = relationship("User", back_populates="workout_sessions")
    # Assuming the Workout model has a 'workout_sessions' back_populates relationship
    workout = relationship("Workout", back_populates="workout_sessions")

    def __repr__(self):
        return (f"<WorkoutSession(id={self.id}, user_id={self.user_id}, "
                f"workout_id={self.workout_id}, status='{self.status}', "
                f"start_time={self.start_time})>")