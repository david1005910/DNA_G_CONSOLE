import joblib
import os
from typing import Optional, Tuple, List
try:
    from lime.lime_text import LimeTextExplainer
except ImportError:
    LimeTextExplainer = None

class XAIService:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.pipeline = None
        self.feature_names = None
        self.explainer = None
        self._load_components()

    def _load_components(self) -> bool:
        """모델(raw classifier), 스케일러, feature 이름을 로드합니다."""
        model_path = os.path.join(self.model_dir, "dna_classifier.joblib")
        scaler_path = os.path.join(self.model_dir, "scaler_rf.joblib")
        feature_path = os.path.join(self.model_dir, "feature_names.joblib")

        try:
            if os.path.exists(model_path):
                self.classifier = joblib.load(model_path)
            
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                
            if os.path.exists(feature_path):
                self.feature_names = joblib.load(feature_path)

            # 전처리기 초기화
            from dna_app.services.feature_extractor import BiologicalFeatureExtractor
            self.extractor = BiologicalFeatureExtractor(kmer_size=3)

            if self.classifier and LimeTextExplainer:
                self.explainer = LimeTextExplainer(class_names=self.classifier.classes_)
            
            return True
        except Exception as e:
            print(f"[XAI Service] Error loading components: {e}")
            return False

    def reload_model(self) -> bool:
        """모델 및 컴포넌트를 다시 로드합니다."""
        print(f"Attempting to reload XAI service components from '{self.model_dir}'...")
        success = self._load_components()
        if success:
            print("XAI Service reloaded successfully.")
        return success

    def explain_prediction(self, dna_sequence: str) -> dict:
        """LIME을 사용하여 예측 결과를 설명합니다."""
        if not self.classifier or not self.explainer:
            return {"error": "XAI service not ready (model or LIME missing)"}

        def predict_fn(texts: List[str]):
            # LIME은 문자열 리스트를 입력으로 주므로 전체 파이프라인 수동 적용
            X_feat = self.extractor.transform(texts)
            X_scaled = self.scaler.transform(X_feat)
            return self.classifier.predict_proba(X_scaled)

        try:
            exp = self.explainer.explain_instance(
                dna_sequence, 
                predict_fn, 
                num_features=5
            )
            return {"explanation": exp.as_list()}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
