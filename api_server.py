# filename: api_server.py
import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from services.record_service import RecordService
from services.ml_service import MLService
from database.db_manager import DatabaseManager
from train_model import train_and_save_model

# --- 애플리케이션 초기화 ---
app = Flask(__name__)
# 로컬 개발 환경에서 React 앱(다른 포트)의 요청을 허용하기 위해 CORS 설정
CORS(app)

# --- 전역 변수 및 설정 ---
DB_FILE = "database/genetics.db"
MODEL_FILE = "ml_models/dna_classifier.joblib"
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

# --- 서비스 인스턴스 생성 ---
# API 서버가 시작될 때 모델 학습 및 서비스 초기화를 수행합니다.
if not os.path.exists(MODEL_FILE):
    print("[API Server] Model not found. Starting training...")
    train_and_save_model(MODEL_FILE)
else:
    print("[API Server] Existing model found.")

db_manager = DatabaseManager(db_path=DB_FILE)
record_service = RecordService(db_manager=db_manager)
ml_service = MLService(model_path=MODEL_FILE)
print("[API Server] All services initialized. Server is ready.")


# --- Helper Function ---
def format_record(record):
    """GeneticRecord 객체를 JSON 직렬화 가능한 dict로 변환합니다."""
    if not record:
        return None
    return {
        "record_id": record.record_id,
        "dna_sequence": record.dna_sequence,
        "birth_time": record.birth_time.isoformat(),
        "death_time": record.death_time.isoformat() if record.death_time else None,
    }

# --- API Endpoints ---
@app.route("/api/records", methods=["GET"])
def get_all_records():
    """모든 유전 정보 기록을 조회합니다."""
    records = record_service.list_all_records()
    return jsonify([format_record(r) for r in records])

@app.route("/api/records", methods=["POST"])
def create_record():
    """새로운 유전 정보 기록을 생성합니다."""
    data = request.get_json()
    dna_sequence = data.get("dna_sequence")

    if not dna_sequence:
        return jsonify({"error": "DNA sequence is required"}), 400

    try:
        new_record = record_service.create_record(dna_sequence)
        if new_record is None:
             return jsonify({"error": "Invalid DNA sequence. Must contain only A, T, C, G."}), 400
        
        # 생성된 DNA를 AI 모델로 분석
        predicted_type = ml_service.predict_dna_type(new_record.dna_sequence)
        
        response_data = format_record(new_record)
        response_data["predicted_type"] = predicted_type
        
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/records/<string:record_id>/terminate", methods=["PUT"])
def terminate_record(record_id):
    """특정 유전 정보 기록을 소멸 상태로 변경합니다."""
    success = record_service.terminate_record(record_id)
    if success:
        terminated_record = record_service.find_record_by_id(record_id)
        return jsonify(format_record(terminated_record))
    else:
        # 이미 소멸되었거나 ID가 없는 경우
        record = record_service.find_record_by_id(record_id)
        if record:
             return jsonify({"message": "Record was already terminated"}), 200
        return jsonify({"error": "Record not found"}), 404
        
if __name__ == "__main__":
    # main.py 대신 이 파일을 실행하여 백엔드 서버를 구동합니다.
    app.run(debug=True, port=5001)

