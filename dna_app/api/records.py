from flask import Blueprint, jsonify, request, current_app
import uuid
from datetime import datetime
import sqlite3

bp = Blueprint('records', __name__)

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DB_FILE'])
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/records', methods=['POST'])
def create_record():
    data = request.json
    dna_sequence = data.get('dna_sequence')
    record_type = data.get('record_type', 'DNA')
    
    if not dna_sequence:
        return jsonify({"error": "DNA sequence is required"}), 400
    
    # Prediction
    prediction = current_app.ml_service.predict(dna_sequence)
    
    record_id = str(uuid.uuid4())
    birth_time = datetime.now()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure column exists (Migration fallback)
    try:
        cursor.execute("SELECT record_type FROM genetic_records LIMIT 1")
    except:
        cursor.execute("ALTER TABLE genetic_records ADD COLUMN record_type TEXT DEFAULT 'DNA'")
        
    cursor.execute(
        "INSERT INTO genetic_records (record_id, dna_sequence, birth_time, record_type) VALUES (?, ?, ?, ?)",
        (record_id, dna_sequence, birth_time, record_type)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "record_id": record_id,
        "predicted_type": prediction["predicted_type"],
        "confidence": prediction["confidence"],
        "record_type": record_type
    }), 201

@bp.route('/records', methods=['GET'])
def get_records():
    type_filter = request.args.get('type') # Optional filter
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure column exists
    try:
        cursor.execute("SELECT record_type FROM genetic_records LIMIT 1")
    except:
         # If table/column error, just ignore filter or handle gracefully
         pass

    query = "SELECT * FROM genetic_records"
    params = []
    
    if type_filter:
        query += " WHERE record_type = ?"
        params.append(type_filter)
        
    query += " ORDER BY birth_time DESC LIMIT 50"
    
    try:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
    except:
        # Fallback if column missing
        cursor.execute("SELECT * FROM genetic_records ORDER BY birth_time DESC LIMIT 50")
        rows = cursor.fetchall()
    
    records = []
    for row in rows:
        prediction = current_app.ml_service.predict(row['dna_sequence'])
        # Handle missing column in row if something went wrong
        r_type = row['record_type'] if 'record_type' in row.keys() else 'DNA'
        
        records.append({
            "record_id": row['record_id'],
            "dna_sequence": row['dna_sequence'],
            "birth_time": row['birth_time'],
            "death_time": row['death_time'],
            "predicted_type": prediction["predicted_type"],
            "record_type": r_type
        })
    conn.close()
    return jsonify(records)

@bp.route('/records/fetch_samples', methods=['POST'])
def fetch_samples():
    data = request.json or {}
    count = data.get('count', 10)
    record_type = data.get('record_type', 'DNA')
    sort_by = data.get('sort', 'relevance')
    
    # NCBI Meta Info
    meta_info = current_app.record_service.get_ncbi_meta(record_type=record_type)
    
    # Fetching logic
    num_fetched = current_app.record_service.fetch_real_samples_from_ncbi(count=count, record_type=record_type, sort=sort_by)
    
    return jsonify({
        "status": "success", 
        "message": f"Successfully fetched {len(num_fetched)} {record_type} samples.",
        "added": len(num_fetched),
        "total_available": meta_info['total_count'],
        "type": record_type
    })

@bp.route('/records/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) as count FROM genetic_records")
    total = cursor.fetchone()['count']
    
    # DNA count
    try:
        cursor.execute("SELECT COUNT(*) as count FROM genetic_records WHERE record_type='DNA'")
        dna = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM genetic_records WHERE record_type='RNA'")
        rna = cursor.fetchone()['count']
    except:
        dna = total
        rna = 0
        
    conn.close()
    return jsonify({
        "total_in_db": total,
        "dna_count": dna,
        "rna_count": rna
    })

@bp.route('/records/ncbi_meta', methods=['GET'])
def get_ncbi_meta():
    record_type = request.args.get('type', 'DNA')
    meta_info = current_app.record_service.get_ncbi_meta(record_type=record_type)
    return jsonify(meta_info)
