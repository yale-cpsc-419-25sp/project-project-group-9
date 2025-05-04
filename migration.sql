-- migration.sql
-- This script makes necessary changes to support multiple profiles per login

-- Add cas_username column if it doesn't exist
PRAGMA foreign_keys=off;

-- Create a backup of Users table
CREATE TABLE Users_backup (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cas_username TEXT,      -- This is the key field for supporting multiple profiles
    hashed_password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    pronoun TEXT,
    residential_college TEXT,
    college_year TEXT,
    headshot_path TEXT,
    extracurriculars TEXT,
    work_experience TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy data from existing Users table
INSERT INTO Users_backup(user_id, hashed_password, email, name, pronoun, residential_college, college_year,
                        headshot_path, extracurriculars, work_experience, bio, created_at, updated_at)
SELECT user_id, hashed_password, name, pronoun, residential_college, college_year,
       headshot_path, extracurriculars, work_experience, bio, created_at, updated_at
FROM Users;

-- Drop the original table
DROP TABLE Users;

-- Rename the backup table
ALTER TABLE Users_backup RENAME TO Users;

-- Create indices
CREATE INDEX idx_users_cas_username ON Users(cas_username);

PRAGMA foreign_keys=on;
