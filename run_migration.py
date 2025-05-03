#!/usr/bin/env python3
# run_migration.py - Run the database migration for multiple profiles

import sqlite3
import os

def run_migration():
    print("Starting database migration for multiple profiles support...")
    
    if not os.path.exists('lux.sqlite'):
        print("Database file not found.")
        return
    
    # Backup the database
    try:
        import shutil
        backup_file = 'lux.sqlite.bak'
        shutil.copy2('lux.sqlite', backup_file)
        print(f"Database backed up to {backup_file}")
    except Exception as e:
        print(f"Failed to backup database: {e}")
        return
    
    # Connect to the database
    conn = sqlite3.connect('lux.sqlite')
    cursor = conn.cursor()
    
    try:
        # Check if cas_username column exists
        cursor.execute("PRAGMA table_info(Users)")
        columns = cursor.fetchall()
        has_cas_username = any(col[1] == 'cas_username' for col in columns)
        
        if has_cas_username:
            print("The cas_username column already exists, no need to run migration.")
            return
        
        # Turn off foreign keys for migration
        cursor.execute("PRAGMA foreign_keys=off")
        
        # Create backup table with the new column
        cursor.execute('''
        CREATE TABLE Users_backup (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cas_username TEXT,
            hashed_password TEXT NOT NULL,
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
        )
        ''')
        
        # Copy data from old table
        cursor.execute('''
        INSERT INTO Users_backup(user_id, hashed_password, name, pronoun, 
                              residential_college, college_year, headshot_path, 
                              extracurriculars, work_experience, bio, 
                              created_at, updated_at)
        SELECT user_id, hashed_password, name, pronoun, 
               residential_college, college_year, headshot_path, 
               extracurriculars, work_experience, bio, 
               created_at, updated_at
        FROM Users
        ''')
        
        # Drop old table
        cursor.execute("DROP TABLE Users")
        
        # Rename backup table
        cursor.execute("ALTER TABLE Users_backup RENAME TO Users")
        
        # Create index
        cursor.execute("CREATE INDEX idx_users_cas_username ON Users(cas_username)")
        
        # Turn foreign keys back on
        cursor.execute("PRAGMA foreign_keys=on")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        print("Please restore from backup.")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()