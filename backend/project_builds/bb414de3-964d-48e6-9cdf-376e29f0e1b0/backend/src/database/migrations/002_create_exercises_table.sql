CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    instructions TEXT,
    muscle_groups JSONB DEFAULT '[]'::jsonb NOT NULL, -- Stores an array of muscle group names as JSONB
    media_urls JSONB DEFAULT '[]'::jsonb NOT NULL,    -- Stores an array of media (image/video) URLs as JSONB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create a function to update the 'updated_at' column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to call the function before each update on the exercises table
CREATE TRIGGER update_exercises_updated_at
BEFORE UPDATE ON exercises
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();