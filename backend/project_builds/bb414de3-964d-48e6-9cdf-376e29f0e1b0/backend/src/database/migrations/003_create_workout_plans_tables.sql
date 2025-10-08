-- Migration: 003_create_workout_plans_tables.sql

-- Create the workoutPlans table
CREATE TABLE workoutPlans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userId UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
        FOREIGN KEY (userId)
        REFERENCES users(id)
        ON DELETE CASCADE, -- If a user is deleted, their workout plans are also deleted
    
    CONSTRAINT uq_user_workout_plan_name
        UNIQUE (userId, name) -- Ensure a user cannot have two workout plans with the same name
);

-- Create a trigger to update the 'updatedAt' column automatically
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updatedAt = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_workoutPlans_updatedAt
BEFORE UPDATE ON workoutPlans
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Create the workoutPlanExercises junction table
CREATE TABLE workoutPlanExercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workoutPlanId UUID NOT NULL,
    exerciseId UUID NOT NULL,
    orderIndex INT NOT NULL, -- To define the sequence of exercises within a plan
    sets INT NOT NULL CHECK (sets > 0), -- Suggested number of sets, must be positive
    reps INT NOT NULL CHECK (reps > 0), -- Suggested number of repetitions, must be positive
    restTimeSeconds INT NOT NULL CHECK (restTimeSeconds >= 0), -- Suggested rest time in seconds, can be 0 or more
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workout_plan
        FOREIGN KEY (workoutPlanId)
        REFERENCES workoutPlans(id)
        ON DELETE CASCADE, -- If a workout plan is deleted, its associated exercises are also deleted
    
    CONSTRAINT fk_exercise
        FOREIGN KEY (exerciseId)
        REFERENCES exercises(id)
        ON DELETE CASCADE, -- If an exercise is deleted, its association with workout plans is also deleted

    CONSTRAINT uq_workout_plan_exercise
        UNIQUE (workoutPlanId, exerciseId), -- An exercise can only be added once per workout plan
    
    CONSTRAINT uq_workout_plan_order_index
        UNIQUE (workoutPlanId, orderIndex) -- Ensure no two exercises have the same order within a plan
);

-- Create a trigger to update the 'updatedAt' column automatically for workoutPlanExercises
CREATE TRIGGER update_workoutPlanExercises_updatedAt
BEFORE UPDATE ON workoutPlanExercises
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Add comments for better documentation (optional but good practice)
COMMENT ON TABLE workoutPlans IS 'Stores definitions of user-created workout routines.';
COMMENT ON COLUMN workoutPlans.id IS 'Unique identifier for the workout plan.';
COMMENT ON COLUMN workoutPlans.userId IS 'ID of the user who owns this workout plan (FK to users.id).';
COMMENT ON COLUMN workoutPlans.name IS 'Name of the workout plan.';
COMMENT ON COLUMN workoutPlans.description IS 'Optional detailed description of the workout plan.';
COMMENT ON COLUMN workoutPlans.createdAt IS 'Timestamp when the workout plan was created.';
COMMENT ON COLUMN workoutPlans.updatedAt IS 'Timestamp when the workout plan was last updated.';

COMMENT ON TABLE workoutPlanExercises IS 'Junction table linking workout plans to exercises, including specific parameters for each exercise within a plan.';
COMMENT ON COLUMN workoutPlanExercises.id IS 'Unique identifier for the association.';
COMMENT ON COLUMN workoutPlanExercises.workoutPlanId IS 'ID of the workout plan (FK to workoutPlans.id).';
COMMENT ON COLUMN workoutPlanExercises.exerciseId IS 'ID of the exercise (FK to exercises.id).';
COMMENT ON COLUMN workoutPlanExercises.orderIndex IS 'The sequential order of this exercise within the workout plan.';
COMMENT ON COLUMN workoutPlanExercises.sets IS 'Suggested number of sets for this exercise within the plan.';
COMMENT ON COLUMN workoutPlanExercises.reps IS 'Suggested number of repetitions for this exercise within the plan.';
COMMENT ON COLUMN workoutPlanExercises.restTimeSeconds IS 'Suggested rest time in seconds after completing a set of this exercise.';
COMMENT ON COLUMN workoutPlanExercises.createdAt IS 'Timestamp when the exercise was added to the workout plan.';
COMMENT ON COLUMN workoutPlanExercises.updatedAt IS 'Timestamp when the exercise parameters within the plan were last updated.';