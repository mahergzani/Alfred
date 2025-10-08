from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    muscle_group = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)  # e.g., 'beginner', 'intermediate', 'expert'
    video_url = Column(String, nullable=True) # Optional URL to an exercise video

    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}', muscle_group='{self.muscle_group}')>"