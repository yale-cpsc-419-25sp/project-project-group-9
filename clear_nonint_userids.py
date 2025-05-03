import sqlite3

DB_PATH = 'lux.sqlite'

def clear_nonint_userids(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Find all tables in the database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]

    # For each table that has a 'user_id' column, delete non-integer entries
    for table in tables:
        cur.execute(f"PRAGMA table_info('{table}');")
        cols = [col_info[1] for col_info in cur.fetchall()]
        if 'user_id' in cols:
            print(f"Cleaning table: {table}")
            cur.execute(
                f"DELETE FROM \"{table}\" WHERE user_id NOT GLOB '[0-9]*';"
            )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    clear_nonint_userids(DB_PATH)
    print("Finished removing non-integer user_id entries.")