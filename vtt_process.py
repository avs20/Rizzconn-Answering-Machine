import os
import sqlite3
import pandas as pd
from nltk.tokenize import word_tokenize
import re

# Function to chunk text into specified size with overlap and keep track of timestamps
def chunk_text_with_timestamps(text, start_ts, end_ts, chunk_size=256, overlap=0.5):
    words = word_tokenize(text)
    chunks = []
    step = int(chunk_size * (1 - overlap))
    num_chunks = (len(words) - chunk_size + step) // step
    
    for i in range(0, num_chunks * step, step):
        chunk = words[i:i + chunk_size]
        if len(chunk) < chunk_size:
            break
        chunk_start_ts = start_ts
        chunk_end_ts = end_ts  # Placeholder for real calculation, you might need to calculate it based on word timings
        chunks.append((' '.join(chunk), chunk_start_ts, chunk_end_ts))
    
    return chunks

# Function to read VTT files from the database
def read_vtt_files_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT folder_name, file_name FROM vtt_files")
    vtt_files = cursor.fetchall()
    conn.close()
    return vtt_files


# Function to process VTT file and extract chunks with timestamps
def process_vtt_file(file_path, chunk_size=256, overlap=0.5):
    with open(file_path, 'r') as file:
        vtt_data = file.read()
    
    # Regular expression to match the VTT format
    pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?): (.*?)\n"
    matches = re.findall(pattern, vtt_data, re.DOTALL)
    
    # Merge text by the same user and create chunks with timestamps
    data = []
    current_user = None
    current_text = ""
    start_ts = None

    for match in matches:
        id, start, end, user, text = match
        if user != current_user:
            if current_user is not None:
                data.append((current_user, current_text, start_ts, previous_end))
            current_user = user
            current_text = text
            start_ts = start
        else:
            current_text += " " + text
        previous_end = end

    if current_user is not None:
        data.append((current_user, current_text, start_ts, previous_end))

    chunks = []
    chunk_id = 1
    for user, text, start_ts, end_ts in data:
        text_chunks = chunk_text_with_timestamps(text, start_ts, end_ts, chunk_size, overlap)
        for chunk, chunk_start_ts, chunk_end_ts in text_chunks:
            chunks.append((chunk_id, chunk, chunk_start_ts, chunk_end_ts, user))
            chunk_id += 1

    return chunks

# Function to save chunks to the database
def save_chunks_to_db(db_path, folder_name, file_name, chunks):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS text_chunks (
            id INTEGER PRIMARY KEY,
            talkname TEXT,
            filename TEXT,
            chunkid INTEGER,
            chunk TEXT,
            start_ts TEXT,
            end_ts TEXT,
            username TEXT
        )
    ''')
    
    for chunk_id, chunk, chunk_start_ts, chunk_end_ts, user in chunks:
        cursor.execute('''
            INSERT INTO text_chunks (talkname, filename, chunkid, chunk, start_ts, end_ts, username)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (folder_name, file_name, chunk_id, chunk, chunk_start_ts, chunk_end_ts, user))
    
    conn.commit()
    conn.close()

# Main script to process all VTT files and save chunks
root_dir = '/Users/t0mkaka/Desktop/Network/vtt_files'  # Replace with the path to your root folder
db_path = 'rag.db'   # Replace with the path to your SQLite database

vtt_files = read_vtt_files_from_db(db_path)

for folder_name, file_name in vtt_files:
    file_path = os.path.join(root_dir, file_name)
    if os.path.exists(file_path):
        chunks = process_vtt_file(file_path)
        save_chunks_to_db(db_path, folder_name, file_name, chunks)

print("Processed and saved all text chunks with timestamps and usernames to the database.")
