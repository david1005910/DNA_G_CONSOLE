from flask import Blueprint, jsonify, current_app, request
import sqlite3
import os

bp = Blueprint('database', __name__)

def get_db_connection():
    db_path = current_app.config['DB_FILE']
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/database/tables', methods=['GET'])
def get_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"status": "success", "tables": tables})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/database/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Table not found"}), 404

        # Total Count
        cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
        total_count = cursor.fetchone()['total']

        # Schema
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [dict(row) for row in cursor.fetchall()]
        
        # Paginated Data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?;", (per_page, offset))
        rows = [dict(row) for row in cursor.fetchall()]

        # Masking for sensitive data
        if table_name == 'system_metadata':
            for row in rows:
                if row['key'] == 'gemini_api_key' and row['value']:
                    val = row['value']
                    row['value'] = "sk-" + "*" * (len(val) - 6) if len(val) > 6 else "***"
        
        # Truncate long text fields for user_documents
        if table_name == 'user_documents':
            for row in rows:
                if row.get('content') and len(row['content']) > 100:
                    row['content'] = row['content'][:100] + '...'
                if row.get('enhanced_content') and len(row['enhanced_content']) > 100:
                    row['enhanced_content'] = row['enhanced_content'][:100] + '...'
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "table": table_name,
            "columns": columns,
            "rows": rows,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_rows": total_count,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
