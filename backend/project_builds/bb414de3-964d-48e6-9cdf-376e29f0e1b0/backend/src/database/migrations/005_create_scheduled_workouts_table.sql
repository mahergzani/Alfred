CREATE TABLE scheduledWorkouts (
    id SERIAL PRIMARY KEY,
    userId INT NOT NULL,
    workoutPlanId INT NOT NULL,
    scheduledDateTime TIMESTAMP WITH TIME ZONE NOT NULL,
    externalCalendarEventId VARCHAR(255), -- Storing an ID from an external calendar system (e.g., Google Calendar event ID)
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
        FOREIGN KEY (userId)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_workout_plan
        FOREIGN KEY (workoutPlanId)
        REFERENCES workoutPlans(id)
        ON DELETE CASCADE
);

-- Create an index on userId and scheduledDateTime for faster lookup of a user's scheduled workouts
CREATE INDEX idx_scheduled_workouts_user_datetime ON scheduledWorkouts (userId, scheduledDateTime);

-- Create a function to update the 'updatedAt' column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updatedAt = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to call the function before each update on the 'scheduledWorkouts' table
CREATE TRIGGER update_scheduled_workouts_updated_at
BEFORE UPDATE ON scheduledWorkouts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();