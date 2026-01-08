import sys
import os

# Add project root to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

from train_model import retrain_model_from_db, train_sequence_model
from config import config

def verify_retraining():
    db_path = config.DB_FILE
    model_path = config.MODEL_FILE
    
    print("--- 1. Basic Model Retraining ---")
    success, msg = retrain_model_from_db(model_path, db_path)
    print(f"Success: {success}, Message: {msg}")
    
    print("\n--- 2. Sequence Model Training ---")
    success, msg = train_sequence_model(model_path, db_path)
    print(f"Success: {success}, Message: {msg}")

    print("\n--- 3. Verify Files ---")
    files = [
        "dna_classifier.joblib",
        "scaler_rf.joblib",
        "sequence_model.joblib",
        "scaler_gb.joblib",
        "feature_names.joblib",
        "inference.py"
    ]
    all_found = True
    for f in files:
        fpath = os.path.join(config.MODEL_DIR, f)
        exists = os.path.exists(fpath)
        print(f"File {f}: {'Found' if exists else 'MISSING'}")
        if not exists: all_found = False
    
    if all_found:
        print("\n✅ Verification SUCCESS: All portable components generated.")
    else:
        print("\n❌ Verification FAILED: Some components are missing.")

if __name__ == "__main__":
    verify_retraining()
