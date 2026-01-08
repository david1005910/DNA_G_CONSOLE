# filename: main.py
import random
import time
import os
from services.record_service import RecordService
from services.ml_service import MLService
from database.db_manager import DatabaseManager
from train_model import train_initial_model # 모델 학습 함수 임포트

def generate_random_dna(length: int) -> str:
    """지정된 길이의 무작위 DNA 서열을 생성합니다."""
    return "".join(random.choice("ATCG") for _ in range(length))

if __name__ == "__main__":
    DB_FILE = "database/genetics.db"
    MODEL_FILE = "ml_models/dna_classifier.joblib"
    
    # 데모를 위해 실행 시 항상 깨끗한 상태에서 시작
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    if os.path.exists(MODEL_FILE):
        os.remove(MODEL_FILE)
        
    # 데이터베이스 및 모델 디렉토리 생성
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True) # ml_models 디렉토리 생성 보장
    
    # 1. AI 모델 학습 (애플리케이션 시작 시 수행)
    print("--- [Step 1: AI Model Training] ---")
    train_initial_model(MODEL_FILE)
    print("-" * 35 + "\n")

    # 2. 서비스 초기화: DB 매니저, 기록 서비스, ML 서비스
    print("--- [Step 2: Initializing Services] ---")
    db_manager = DatabaseManager(db_path=DB_FILE)
    record_service = RecordService(db_manager=db_manager)
    ml_service = MLService(model_path=MODEL_FILE)
    print("-" * 35 + "\n")

    # 3. 새로운 유전 정보 생성 및 AI 분석
    print("--- [Step 3: Creating Records and Performing AI Analysis] ---")
    # AI가 'Type A'로 예측할 확률이 높은 DNA 서열 생성 (GCG 모티프 많이 포함)
    dna_type_a_candidate = generate_random_dna(70) + "GCG" * 10 
    # AI가 'Type B'로 예측할 확률이 높은 DNA 서열 생성 (GCG 모티프 적게 포함)
    dna_type_b_candidate = generate_random_dna(100)

    # 첫 번째 기록 생성 및 분석
    record1 = record_service.create_record(dna_type_a_candidate)
    if record1 and ml_service.is_ready():
        predicted_type = ml_service.predict_dna_type(record1.dna_sequence)
        print(f"  -> AI Analysis Result for {record1.record_id[:8]}...: Predicted as '{predicted_type}'")

    time.sleep(1) # 시간차

    # 두 번째 기록 생성 및 분석
    record2 = record_service.create_record(dna_type_b_candidate)
    if record2 and ml_service.is_ready():
        predicted_type = ml_service.predict_dna_type(record2.dna_sequence)
        print(f"  -> AI Analysis Result for {record2.record_id[:8]}...: Predicted as '{predicted_type}'")
    print("-" * 35 + "\n")

    # 4. 특정 기록 소멸 처리
    if record1:
        print(f"--- [Step 4: Terminating a Record] ---")
        record_service.terminate_record(record1.record_id)
        print("-" * 35 + "\n")

    # 5. 최종 데이터베이스 상태 확인
    print("--- [Step 5: Final State of the Database] ---")
    final_records = record_service.list_all_records()
    if final_records:
        for record in final_records:
            print(f" - {record}")
    else:
        print("No records found.")
    print("-" * 35 + "\n")

    # 6. 데이터베이스 연결 종료
    db_manager.close()
