--migrate_add_cas_username.sql
ALTER TABLE Users
ADD COLUMN cas_username TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_cas_username
ON Users(cas_username);
