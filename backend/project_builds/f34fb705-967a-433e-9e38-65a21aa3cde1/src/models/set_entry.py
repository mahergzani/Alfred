from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# It's common practice to have a single Base for all models.
# If this `Base` is defined elsewhere (e.g., in a `database.py` file),
# it should be imported from there. For this isolated model file,
# we define it here, assuming other models would import it.
Base = declarative_base()

class SetEntry(Base):
    """
    ORM model for recording performance data for each set within a workout session.
    """
    __tablename__ = 'set_entries'

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to the WorkoutSession this set entry belongs to
    workout_session_id = Column(Integer, ForeignKey('workout_sessions.id'), nullable=False)
    
    # Foreign key to the Exercise performed in this set
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False)
    
    set_number = Column(Integer, nullable=False) # e.g., 1 for the first set, 2 for the second, etc.
    weight = Column(Float, nullable=False) # Weight lifted (e.g., in kg or lbs)
    reps = Column(Integer, nullable=False) # Number of repetitions
    rpe = Column(Float, nullable=True) # Rate of Perceived Exertion (e.g., 1-10 scale), optional
    
    # Timestamp when the set was performed, defaults to UTC now for timezone consistency
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    notes = Column(String, nullable=True) # Optional notes for the set

    # Relationships to other models (assuming WorkoutSession and Exercise models exist)
    # This allows easy navigation between related objects in the ORM
    workout_session = relationship("WorkoutSession", back_populates="set_entries")
    exercise = relationship("Exercise", back_populates="set_entries")

    def __repr__(self):
        return (f"<SetEntry(id={self.id}, workout_session_id={self.workout_session_id}, "
                f"exercise_id={self.exercise_id}, set_number={self.set_number}, "
                f"weight={self.weight}, reps={self.reps}, rpe={self.rpe})>")