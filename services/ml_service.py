# filename: services/ml_service.py
import os
import joblib
from typing import Optional

class MLService:
    """
    DNA 서열 분석을 위한 머신러닝 모델을 관리하고 예측을 수행하는 서비스.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._model = self._load_model()
        if self._model:
            print(f"ML model loaded successfully from '{self.model_path}'")
        else:
            print(f"Warning: ML model could not be loaded from '{self.model_path}'. Predictions will not be available.")

    def _load_model(self) -> Optional[object]:
        """지정된 경로에서 직렬화된 모델 객체를 로드합니다."""
        try:
            if os.path.exists(self.model_path):
                return joblib.load(self.model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
        return None

    def is_ready(self) -> bool:
        """모델이 성공적으로 로드되었는지 확인합니다."""
        return self._model is not None

    def predict_dna_type(self, dna_sequence: str) -> Optional[str]:
        """
        주어진 DNA 서열의 유형을 예측합니다.
        
        :param dna_sequence: 분석할 DNA 서열 문자열
        :return: 예측된 유형 ('Type A', 'Type B' 등) 또는 모델이 없을 경우 None
        """
        if not self.is_ready():
            return "Prediction unavailable"
        
        # 모델은 리스트 형태의 입력을 기대하므로, 단일 시퀀스를 리스트에 담아 전달
        try:
            prediction = self._model.predict([dna_sequence])
            return prediction[0]
        except Exception as e:
            print(f"Error during prediction: {e}")
            return "Prediction failed"

