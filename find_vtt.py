import os
import sqlite3

# Function to collect all VTT filenames and their folder names
def collect_vtt_files(root_dir):
    vtt_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.vtt'):
                folder_name = os.path.basename(dirpath)
                vtt_files.append((folder_name, file))
    return vtt_files

# Function to save the collected data into an SQLite database
def save_to_sqlite(db_path, vtt_files):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vtt_files (
            id INTEGER PRIMARY KEY,
            folder_name TEXT,
            file_name TEXT
        )
    ''')
    
    cursor.executemany('INSERT INTO vtt_files (folder_name, file_name) VALUES (?, ?)', vtt_files)
    conn.commit()
    conn.close()

# Example usage
root_dir = '/Users/t0mkaka/Library/CloudStorage/OneDrive-Personal/Siolabs/AI Woodstock'  # Replace with the path to your root folder
db_path = 'rag.db'   # Replace with the path to your SQLite database

vtt_files = collect_vtt_files(root_dir)
save_to_sqlite(db_path, vtt_files)

print(f"Collected {len(vtt_files)} VTT files and saved to database: {db_path}")
