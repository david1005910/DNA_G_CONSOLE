from flask import Blueprint, jsonify, current_app, send_file, request
import os
import sqlite3
import zipfile
import io
import csv
from datetime import datetime

bp = Blueprint('system', __name__)

@bp.route('/docs/report', methods=['GET'])
def get_report():
    from flask import request
    lang = request.args.get('lang', 'en')
    filename = f'report_{lang}.md'
    try:
        docs_path = os.path.join(os.getcwd(), 'docs', filename)
        if not os.path.exists(docs_path):
            return jsonify({"content": f"{filename} not found."}), 404
        
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/system/config', methods=['GET', 'POST'])
def handle_config():
    try:
        db_path = current_app.config['DB_FILE']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if request.method == 'POST':
            data = request.json
            if 'gemini_api_key' in data:
                key = data['gemini_api_key']
                cursor.execute("""
                    INSERT INTO system_metadata (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, ('gemini_api_key', key))
                conn.commit()
                conn.close()
                return jsonify({"status": "success", "message": "Configuration saved"})
            conn.close()
            return jsonify({"status": "error", "message": "No valid config keys provided"}), 400
        else:
            # GET
            cursor.execute("SELECT value FROM system_metadata WHERE key = ?", ('gemini_api_key',))
            row = cursor.fetchone()
            conn.close()
            
            key = row[0] if row else None
            masked_key = ""
            if key:
                masked_key = "sk-" + "*" * (len(key) - 6) if len(key) > 6 else "***"
            
            return jsonify({
                "status": "success",
                "config": {
                    "gemini_api_key": masked_key,
                    "is_configured": bool(key)
                }
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/system/status', methods=['GET'])
def get_status():
    status = {
        "database": "Connected",
        "ml_model": "Loaded" if current_app.ml_service.model else "Not Found",
        "xai_service": "Ready"
    }
    return jsonify(status)

@bp.route('/system/reset', methods=['POST'])
def reset_system():
    """DB 초기화 및 모델 초기화를 수행합니다."""
    try:
        db_path = current_app.config['DB_FILE']
        model_path = current_app.config['MODEL_FILE']
        
        # 1. DB 초기화 (기존 테이블 삭제 및 재생성)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 3개 테이블 완전 초기화
        tables_to_reset = ["genetic_records", "raw_genetic_captures", "system_metadata"]
        for table in tables_to_reset:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        # 테이블 재생성
        cursor.execute("""
            CREATE TABLE genetic_records (
                record_id TEXT PRIMARY KEY,
                dna_sequence TEXT NOT NULL,
                birth_time DATETIME NOT NULL,
                death_time DATETIME,
                record_type TEXT DEFAULT 'DNA',
                occurrence_count INTEGER DEFAULT 1,
                source_metadata TEXT DEFAULT '[]'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE raw_genetic_captures (
                capture_id TEXT PRIMARY KEY,
                dna_sequence TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                linked_record_id TEXT,
                source_info TEXT,
                FOREIGN KEY(linked_record_id) REFERENCES genetic_records(record_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE system_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        # 2. 모델 파일 삭제 (초기 모델로 돌아가기 위해)
        if os.path.exists(model_path):
            os.remove(model_path)
            
        # 3. 모델 초기 재학습 실행
        from train_model import train_initial_model
        train_initial_model(model_path)
        
        # 4. 서비스 리로드
        current_app.ml_service.reload_model()
        current_app.xai_service.reload_model()
        
        return jsonify({
            "status": "success", 
            "message": "시스템이 공장 초기화되었습니다. 3개 테이블(genetic_records, raw_genetic_captures, system_metadata)이 완전히 초기화되었으며 초기 모델로 복구되었습니다."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/system/download/sandbox', methods=['GET'])
def download_sandbox():
    """Sandbox 디렉토리를 ZIP으로 다운로드 (__pycache__, .pyc 등 제외)"""
    try:
        sandbox_path = os.getcwd()
        memory_file = io.BytesIO()
        
        # 제외할 패턴
        exclude_patterns = ['__pycache__', '.pyc', '.pyo', '.pyd', '.so', '.egg-info', 
                           'venv', '.git', '.DS_Store', '*.log', '.cache']
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(sandbox_path):
                # __pycache__ 등 제외
                dirs[:] = [d for d in dirs if d not in exclude_patterns]
                
                for file in files:
                    # 제외 패턴 체크
                    if any(pattern in file or file.endswith(pattern.replace('*', '')) 
                           for pattern in exclude_patterns):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, sandbox_path)
                    zf.write(file_path, arcname)
        
        memory_file.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'DNA_G_sandbox_{timestamp}.zip'
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/system/download/database', methods=['GET'])
def download_database_csv():
    """genetic_records 테이블을 CSV로 다운로드"""
    try:
        db_path = current_app.config['DB_FILE']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # genetic_records 테이블 조회
        cursor.execute("SELECT * FROM genetic_records")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # CSV 생성
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)  # 헤더
        writer.writerows(rows)    # 데이터
        
        # BytesIO로 변환
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8-sig'))  # BOM 추가 (Excel 호환)
        mem.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'DNA_G_database_{timestamp}.csv'
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
