import joblib
import os
import numpy as np
from dna_app.services.feature_extractor import BiologicalFeatureExtractor

class MLService:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """저장된 모델(raw classifier)과 스케일러를 로드합니다."""
        model_dir = os.path.dirname(self.model_path)
        scaler_path = os.path.join(model_dir, "scaler_rf.joblib")
        
        if os.path.exists(self.model_path) and os.path.exists(scaler_path):
            try:
                # 1. 컴포넌트 로드
                self.classifier = joblib.load(self.model_path)
                self.scaler = joblib.load(scaler_path)
                
                # 2. 전처리 클래스 (커스텀이므로 직접 초기화)
                self.extractor = BiologicalFeatureExtractor(kmer_size=3)
                
                # 3. self.model도 설정 (combined-insights 등에서 체크용)
                self.model = self.classifier
                
                print(f"ML components (classifier + scaler) loaded successfully from '{model_dir}'")
                return True
            except Exception as e:
                print(f"Error loading ML components: {e}")
                self.model = None
                return False
        else:
            print(f"Model/scaler files not found. Predictions will be simulated.")
            self.model = None
            return False

    def reload_model(self) -> bool:
        """모델을 디스크에서 다시 로드합니다 (재학습 후 호출)."""
        print(f"Attempting to reload ML model from '{self.model_path}'...")
        success = self._load_model()
        if success:
            print("ML model reloaded successfully.")
        return success

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, dna_sequence: str):
        """
        DNA 서열의 타입을 예측하고 결과를 반환합니다.
        api/records.py 에서 기대하는 형식인 {'predicted_type': ..., 'confidence': ...} 를 리턴합니다.
        """
        if self.classifier:
            try:
                # 1. 수동 파이프라인 적용
                # DNA 시퀀스 -> 특징 추출 -> 스케일링 -> 예측
                X_features = self.extractor.transform([dna_sequence])
                X_scaled = self.scaler.transform(X_features)
                
                pred_type = self.classifier.predict(X_scaled)[0]
                
                # 2. 확률(Confidence) 계산
                confidence = 0.95
                if hasattr(self.classifier, 'predict_proba'):
                    probs = self.classifier.predict_proba(X_scaled)[0]
                    confidence = float(np.max(probs))
                
                return {
                    "predicted_type": str(pred_type),
                    "confidence": confidence
                }
            except Exception as e:
                print(f"Prediction error: {e}")
                import traceback
                traceback.print_exc()
                return {"predicted_type": "Unknown", "confidence": 0.0}
        else:
            # Fallback (모델이 없을 때)
            is_type_a = "GCG" in dna_sequence.upper()
            return {
                "predicted_type": "Type A (Simulated)" if is_type_a else "Type B (Simulated)",
                "confidence": 0.88
            }

    def predict_dna_type(self, dna_sequence: str) -> str:
        """기존 코드와의 호환성을 위해 유지합니다."""
        res = self.predict(dna_sequence)
        return res["predicted_type"]
