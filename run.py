# Set environment variables BEFORE importing other modules to fix segmentation faults
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['JOBLIB_START_METHOD'] = 'loky'

from dna_app import create_app
import sys
from config import config

# Auto-setup: 학습된 모델이 없으면 자동으로 학습 시작
if not os.path.exists(config.MODEL_FILE):
    print("!! ML Model not found. Starting auto-training... !!")
    try:
        from train_model import train_initial_model
        config.setup_directories()
        train_initial_model(config.MODEL_FILE)
        print("!! Auto-training complete. Starting server... !!\n")
    except Exception as e:
        print(f"!! Error during auto-training: {e}")
        sys.exit(1)

app = create_app()

if __name__ == "__main__":
    # Docker 환경을 위해 0.0.0.0으로 고정합니다.
    # use_reloader=False: Disable Flask reloader to prevent SQLite/joblib memory corruption
    # threaded=False: Disable Flask threading to prevent OpenMP/NumPy C-level thread conflicts (Segmentation Fault)
    app.run(host='0.0.0.0', port=5001, use_reloader=False, threaded=False)
