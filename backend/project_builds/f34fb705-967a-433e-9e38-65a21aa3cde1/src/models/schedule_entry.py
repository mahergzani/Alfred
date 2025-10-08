from datetime import datetime
from src.extensions import db

class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    external_calendar_event_id = db.Column(db.String(255), nullable=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('schedule_entries', lazy=True))
    workout = db.relationship('Workout', backref=db.backref('schedule_entries', lazy=True))

    def __repr__(self):
        return f'<ScheduleEntry {self.id} | User: {self.user_id} | Workout: {self.workout_id} | Scheduled: {self.scheduled_time}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workout_id': self.workout_id,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'completed': self.completed,
            'external_calendar_event_id': self.external_calendar_event_id
        }