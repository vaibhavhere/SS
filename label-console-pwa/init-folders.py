import os
import sqlite3
import argparse

# Database file
DB_FILE = "ss.db"

def create_tables(cursor):
    """Create 'folders' and 'files' tables with ascending indexes."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vehicle TEXT,
            description TEXT,
            price INTEGER,
            folder_id INTEGER,
            FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE CASCADE
        )
    """)

    # Explicit ASC index (though default is already ASC)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_folders_name ON folders(name ASC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name ASC);")

    print("Created tables and indexes (ASC).")

def populate_folders_and_files(cursor, root_path):
    """Populate 'folders' and 'files' tables."""
    for folder_name in sorted(os.listdir(root_path)):  # Ensure ASC order while reading
        folder_path = os.path.join(root_path, folder_name)

        if os.path.isdir(folder_path):
            cursor.execute("INSERT OR IGNORE INTO folders (name) VALUES (?)", (folder_name,))
            cursor.execute("SELECT id FROM folders WHERE name = ?", (folder_name,))
            folder_id = cursor.fetchone()[0]

            for file_name in sorted(os.listdir(folder_path)):  # Ensure ASC order
                if os.path.isfile(os.path.join(folder_path, file_name)):
                    cursor.execute("""
                        INSERT OR IGNORE INTO files (name, vehicle, description, price, folder_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (file_name, file_name, folder_name, 0, folder_id))
    print(f"Populated database from root path: {root_path}")

def main(root_path):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    create_tables(cursor)
    populate_folders_and_files(cursor, root_path)

    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup database for folder/file structure.")
    parser.add_argument("root_path", type=str, help="Path to the root folder.")
    args = parser.parse_args()

    if not os.path.isdir(args.root_path):
        print(f"Error: {args.root_path} is not a valid directory.")
        exit(1)

    main(args.root_path)
