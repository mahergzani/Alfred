from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class WorkoutExercise(Base):
    __tablename__ = 'workout_exercises'

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey('workouts.id', ondelete='CASCADE'), index=True, nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id', ondelete='CASCADE'), index=True, nullable=False)

    suggested_sets = Column(Integer, nullable=False)
    suggested_reps = Column(String, nullable=False)  # e.g., "8-12", "15", "AMRAP"
    suggested_weight = Column(String, nullable=True) # e.g., "50kg", "bodyweight", "N/A", "60-70% 1RM"
    suggested_rest_time_seconds = Column(Integer, nullable=True) # e.g., 60, 90, 120

    # Relationships
    # This creates a many-to-many relationship with extra data (suggested_sets, reps, etc.)
    # from the perspective of Workout, it lists the WorkoutExercises it contains
    workout = relationship("Workout", back_populates="workout_exercises")
    # from the perspective of Exercise, it lists the WorkoutExercises it is part of
    exercise = relationship("Exercise", back_populates="workout_exercises")

    def __repr__(self):
        return (f"<WorkoutExercise(id={self.id}, workout_id={self.workout_id}, "
                f"exercise_id={self.exercise_id}, suggested_sets={self.suggested_sets}, "
                f"suggested_reps='{self.suggested_reps}')>")