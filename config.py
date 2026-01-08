import os

class Config:
    """애플리케이션 설정을 위한 기본 클래스."""
    # BASE_DIR을 현재 파일(config.py)이 있는 위치(프로젝트 루트)로 설정
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # 데이터베이스 설정
    DB_DIR = os.path.join(BASE_DIR, 'database') # database/ 폴더로 변경
    DB_FILE = os.path.join(DB_DIR, "genetics.db")
    
    # 모델 설정
    MODEL_DIR = os.path.join(BASE_DIR, 'ml_models')
    MODEL_FILE = os.path.join(MODEL_DIR, "dna_classifier.joblib")

    @staticmethod
    def setup_directories():
        """필요한 디렉토리를 생성합니다."""
        os.makedirs(Config.DB_DIR, exist_ok=True)
        os.makedirs(Config.MODEL_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

config = DevelopmentConfig()
# 설정 로드 시점에 디렉토리 생성 (선택 사항, 명시적으로 main/run에서 호출하는 것을 권장)
config.setup_directories()
