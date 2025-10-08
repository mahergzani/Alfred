from src.extensions import db
from datetime import datetime

class Workout(db.Model):
    """
    Represents a workout program created by a user.
    """
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=False)
    description = db.Column(db.Text, nullable=True)
    
    # Foreign key to the User model, representing the creator of the workout
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Define relationship to User model
    creator = db.relationship('User', backref=db.backref('created_workouts', lazy=True))

    # Custom status for the workout (e.g., 'draft', 'published', 'archived')
    # Defaulting to 'draft' as it's common for content creation.
    status = db.Column(db.String(50), default='draft', nullable=False)

    # Timestamps for creation and last update
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Workout {self.name} (ID: {self.id})>'