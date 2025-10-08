CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    profile_picture_url VARCHAR(2048),
    bio TEXT,
    phone_number VARCHAR(20),
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL, -- e.g., 'active', 'inactive', 'suspended', 'pending_verification'
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create an index on the email column for faster lookups
CREATE INDEX idx_users_email ON users (email);

-- Optional: Create a function and trigger to automatically update 'updated_at'
-- This is a common practice for auditing changes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();