# filename: setup.py
import os
from train_model import train_initial_model # (수정) 초기 학습 함수로 변경
from config import config

def run_setup():
    """
    로컬 개발 환경에서 모델을 수동으로 생성하기 위한 스크립트.
    Docker 빌드 과정에서는 이 스크립트가 직접 호출되지 않습니다.
    """
    print("--- [Local System Setup] ---")
    model_path = config.MODEL_FILE
    if os.path.exists(model_path):
        print(f"Model already exists at '{model_path}'. Skipping training.")
    else:
        print("Model not found. Starting initial model training for local environment...")
        train_initial_model(model_path) # (수정) 초기 모델 학습 호출
    print("--- [Setup Complete] ---")
    print("For Docker deployment, run 'docker-compose up --build'")
    print("For local execution, ensure your environment has dependencies and run 'python run.py'")

if __name__ == "__main__":
    config.setup_directories() # 디렉토리 생성 호출
    run_setup()
