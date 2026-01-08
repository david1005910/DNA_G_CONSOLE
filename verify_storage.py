import os
import sys
import uuid
from datetime import datetime
from dna_app.database.db_manager import DatabaseManager as DBManager

# Ensure we can import modules
sys.path.append(os.getcwd())

def verify_storage():
    db = DBManager('database/dna_storage.db')
    
    # 1. Create a unique DNA sequence
    unique_seq = f"ATCG-TEST-{str(uuid.uuid4())[:8]}"
    print(f"Testing with sequence: {unique_seq}")

    # 2. Insert First Time
    print("Inserting first time...")
    db.upsert_record(
        record_id=str(uuid.uuid4()),
        dna_sequence=unique_seq,
        birth_time=datetime.now(),
        source_info="test_v1"
    )

    # 3. Verify counts
    cursor = db.conn.cursor()
    cursor.execute("SELECT record_id, occurrence_count FROM genetic_records WHERE dna_sequence = ?", (unique_seq,))
    rec = cursor.fetchone()
    if not rec:
        print("FAIL: Record not found in genetic_records")
        return
    
    rec_id, count = rec
    print(f"Genetic Record: ID={rec_id}, Count={count}")
    
    cursor.execute("SELECT count(*) FROM raw_genetic_captures WHERE dna_sequence = ?", (unique_seq,))
    raw_count = cursor.fetchone()[0]
    print(f"Raw Captures: {raw_count}")

    if count != 1 or raw_count != 1:
        print("FAIL: Initial counts incorrect")
        return

    # 4. Insert Duplicate
    print("Inserting duplicate...")
    db.upsert_record(
        record_id=str(uuid.uuid4()), # This ID should be ignored for the unique record, but linked in raw
        dna_sequence=unique_seq,
        birth_time=datetime.now(),
        source_info="test_v2"
    )

    # 5. Verify counts again
    cursor.execute("SELECT record_id, occurrence_count FROM genetic_records WHERE dna_sequence = ?", (unique_seq,))
    rec_v2 = cursor.fetchone()
    rec_id_v2, count_v2 = rec_v2
    
    cursor.execute("SELECT count(*) FROM raw_genetic_captures WHERE dna_sequence = ?", (unique_seq,))
    raw_count_v2 = cursor.fetchone()[0]

    print(f"Genetic Record v2: ID={rec_id_v2}, Count={count_v2}")
    print(f"Raw Captures v2: {raw_count_v2}")

    if rec_id != rec_id_v2:
         print("FAIL: Record ID changed!")
    elif count_v2 != 2:
         print("FAIL: Occurrence count didn't increment")
    elif raw_count_v2 != 2:
         print("FAIL: Raw capture count didn't increment")
    else:
         print("SUCCESS: Storage verification passed!")
         
    # Check linkage
    cursor.execute("SELECT linked_record_id FROM raw_genetic_captures WHERE dna_sequence = ?", (unique_seq,))
    links = [r[0] for r in cursor.fetchall()]
    print(f"Linked IDs: {links}")
    if all(l == rec_id for l in links):
        print("SUCCESS: All raw captures linked to the correct unique record.")
    else:
        print("FAIL: Linkage mismatch.")

if __name__ == "__main__":
    verify_storage()
