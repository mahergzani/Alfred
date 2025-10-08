CREATE TABLE IF NOT EXISTS completedWorkouts (
    id SERIAL PRIMARY KEY,
    userId INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workoutId INTEGER REFERENCES workouts(id) ON DELETE SET NULL, -- Reference to the original workout template
    name VARCHAR(255) NOT NULL,
    notes TEXT,
    startedAt TIMESTAMP WITH TIME ZONE NOT NULL,
    completedAt TIMESTAMP WITH TIME ZONE, -- Can be NULL if workout is still ongoing
    durationSeconds INTEGER, -- Total duration in seconds
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS completedSets (
    id SERIAL PRIMARY KEY,
    completedWorkoutId INTEGER NOT NULL REFERENCES completedWorkouts(id) ON DELETE CASCADE,
    exerciseId INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    setNumber INTEGER NOT NULL,
    weightKg DECIMAL(10, 2),
    reps INTEGER,
    durationSeconds INTEGER, -- For timed exercises (e.g., plank)
    distanceMeters DECIMAL(10, 2), -- For distance exercises (e.g., run)
    notes TEXT,
    restTimeSeconds INTEGER, -- How long the user rested before this set
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_completedworkouts_userid ON completedWorkouts(userId);
CREATE INDEX IF NOT EXISTS idx_completedworkouts_startedat ON completedWorkouts(startedAt);
CREATE INDEX IF NOT EXISTS idx_completedsets_completedworkoutid ON completedSets(completedWorkoutId);
CREATE INDEX IF NOT EXISTS idx_completedsets_exerciseid ON completedSets(exerciseId);