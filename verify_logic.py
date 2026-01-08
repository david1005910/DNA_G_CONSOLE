import os
import sqlite3
import json
from datetime import datetime
from dna_app.database.db_manager import DatabaseManager

TEST_DB = "test_verify.db"

def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    # create empty db
    conn = sqlite3.connect(TEST_DB)
    conn.close()

def main():
    print("--- 1. Setup Test DB ---")
    setup_test_db()
    db = DatabaseManager(TEST_DB)
    
    # Check Schema
    print("Checking if columns exist...")
    cursor = db.conn.cursor()
    cursor.execute("PRAGMA table_info(genetic_records)")
    columns = [row[1] for row in cursor.fetchall()]
    print("Columns:", columns)
    if "occurrence_count" not in columns or "source_metadata" not in columns:
        print("[FAIL] New columns not found!")
        return
    else:
        print("[PASS] New columns found.")

    print("\n--- 2. Upsert Logic Test ---")
    seq1 = "ATCGATCG" * 20 # 160bp > 100bp
    
    # First Insert
    print("Insert SEQ1 (First time)...")
    db.upsert_record("id1", seq1, datetime.now(), source_info="Header1")
    
    # Verify
    row = cursor.execute("SELECT occurrence_count, source_metadata FROM genetic_records WHERE dna_sequence=?", (seq1,)).fetchone()
    print("Result 1:", row)
    assert row[0] == 1, "Count should be 1"
    meta = json.loads(row[1])
    assert "Header1" in meta, "Metadata should contain Header1"
    
    # Second Upsert (Duplicate)
    print("Insert SEQ1 (Second time - Duplicate)...")
    db.upsert_record("id2", seq1, datetime.now(), source_info="Header2")
    
    # Verify
    row = cursor.execute("SELECT occurrence_count, source_metadata FROM genetic_records WHERE dna_sequence=?", (seq1,)).fetchone()
    print("Result 2:", row)
    assert row[0] == 2, "Count should be 2"
    meta = json.loads(row[1])
    assert len(meta) == 2, "Metadata length should be 2"
    assert "Header2" in meta, "Metadata should contain Header2"
    
    print("[PASS] Upsert logic verified.")
    
    print("\n--- 3. ML Training Logic Check ---")
    # Add another distinct record
    seq2 = "GCGCGCGC" * 20
    db.upsert_record("id3", seq2, datetime.now(), source_info="Header3")
    
    # Total records: 2 distinct sequences.
    # SEQ1: weight 2
    # SEQ2: weight 1
    
    # Mock retrain_model_from_db logic
    records = db.get_all_records()
    print(f"Total fetched from DB: {len(records)}")
    
    sequences = [row[1] for row in records]
    # extracting weights logic
    weights = []
    for row in records:
        w = 1
        if len(row) > 5 and row[5] is not None:
             try:
                 w = int(row[5])
             except:
                 pass
        weights.append(w)
        print(f"Seq: {row[1][:10]}... | Count(Weight): {w}")
    
    assert weights == [2, 1] or weights == [1, 2], f"Weights mismatch. Got {weights}"
    print("[PASS] Weights extraction verified.")

    db.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    print("\nALL TESTS PASSED.")

if __name__ == "__main__":
    main()
