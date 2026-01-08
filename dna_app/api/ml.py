from flask import Blueprint, jsonify, current_app, send_file, request
import joblib
import os
import numpy as np
import io
from datetime import datetime

# train_model 모듈 import 처리
try:
    from train_model import retrain_model_from_db, train_sequence_model
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from train_model import retrain_model_from_db, train_sequence_model

bp = Blueprint('ml', __name__)

@bp.route("/ml/retrain", methods=["POST"])
def trigger_retraining():
    model_path = current_app.config['MODEL_FILE']
    db_path = current_app.config['DB_FILE']
    
    success, message = retrain_model_from_db(model_path, db_path)
    if not success:
        return jsonify({"status": "failed", "message": message}), 400

    ml_reloaded = current_app.ml_service.reload_model()
    current_app.xai_service.reload_model()

    return jsonify({"status": "success", "message": message})


@bp.route("/ml/sequence-train", methods=["POST"])
def trigger_sequence_training():
    """시퀀스 고유 특징 학습 - 메타데이터 기반 바이러스 타입 분류"""
    model_path = current_app.config['MODEL_FILE']
    db_path = current_app.config['DB_FILE']
    
    success, message = train_sequence_model(model_path, db_path)
    if not success:
        return jsonify({"status": "failed", "message": message}), 400

    return jsonify({"status": "success", "message": message})


@bp.route("/ml/sequence-inspect", methods=["GET"])
def inspect_sequence_model():
    """시퀀스 모델 메트릭 조회"""
    model_path = current_app.config['MODEL_FILE']
    model_dir = os.path.dirname(model_path)
    
    sequence_model_path = os.path.join(model_dir, "sequence_model.joblib")
    sequence_metrics_path = os.path.join(model_dir, "sequence_metrics.joblib")
    
    if not os.path.exists(sequence_metrics_path):
        return jsonify({"status": "not_trained", "message": "Sequence model not trained yet."})
    
    try:
        metrics = joblib.load(sequence_metrics_path)
        
        return jsonify({
            "status": "success",
            "model_type": metrics.get("model_type", "Unknown"),
            "accuracy": metrics.get("accuracy", 0),
            "f1_score": metrics.get("f1_score", 0),
            "labels": metrics.get("labels", []),
            "label_distribution": metrics.get("label_distribution", {}),
            "train_size": metrics.get("train_size", 0),
            "test_size": metrics.get("test_size", 0),
            "feature_count": metrics.get("feature_count", 0),
            "trained_at": metrics.get("trained_at", None)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/ml/inspect", methods=["GET"])
def inspect_model():
    """joblib 파일을 직접 열어 모델의 내부 구조( weights, feature_names 등)를 분석합니다."""
    model_path = current_app.config['MODEL_FILE']
    feature_names_path = os.path.join(os.path.dirname(model_path), "feature_names.joblib")
    
    if not os.path.exists(model_path):
        return jsonify({"error": "Model file not found.", "info": {"algorithm": "N/A", "classes": [], "total_features": 0}}), 404

    try:
        # 1. 모델 로드 (Pipeline 또는 standalone classifier)
        model = joblib.load(model_path)
        
        # 2. Feature names 파일 로드
        feature_names = []
        if os.path.exists(feature_names_path):
            feature_names = joblib.load(feature_names_path)

        # 분기: Pipeline인지 standalone classifier인지 확인
        if hasattr(model, 'named_steps'):
            # Pipeline인 경우
            classifier = model.named_steps.get('classifier')
        else:
            # Standalone classifier인 경우 (v1.3+ 이후 저장 방식)
            classifier = model
        
        if classifier is None:
            return jsonify({
                "status": "error", 
                "error": "Classifier not found in model file.",
                "info": {"algorithm": "N/A", "classes": [], "total_features": 0}
            }), 500

        info = {
            "algorithm": type(classifier).__name__ if classifier else "Unknown",
            "classes": classifier.classes_.tolist() if hasattr(classifier, 'classes_') else [],
            "params": classifier.get_params() if hasattr(classifier, 'get_params') else {},
            "total_features": len(feature_names),
            "feature_names_source": "biological_features"
        }
        
        # n_estimators, max_depth 등 주요 하이퍼파라미터 추가
        if hasattr(classifier, 'n_estimators'):
            info["n_estimators"] = classifier.n_estimators
        if hasattr(classifier, 'max_depth'):
            info["max_depth"] = classifier.max_depth

        # 특징 중요도 추출 (feature_names.joblib 기반)
        top_features = []
        if feature_names and hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
            indices = np.argsort(importances)[::-1]
            for i in range(min(20, len(indices))):
                idx = indices[i]
                if idx < len(feature_names):
                    top_features.append({
                        "name": feature_names[idx],
                        "weight": float(importances[idx])
                    })
        
        # Confusion Matrix 및 성능 지표 (학습 시 저장된 데이터가 있다면)
        metrics_path = os.path.join(os.path.dirname(model_path), "training_metrics.joblib")
        training_metrics = None
        if os.path.exists(metrics_path):
            training_metrics = joblib.load(metrics_path)
        
        return jsonify({
            "status": "success",
            "model_path": model_path,
            "info": info,
            "top_features": top_features,
            "extra_feature_names": feature_names[:30] if len(feature_names) > 20 else feature_names,
            "training_metrics": training_metrics
        })

    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@bp.route("/ml/upload-huggingface", methods=["POST"])
def upload_to_huggingface():
    """Hugging Face Hub로 모델 업로드"""
    try:
        from dna_app.services.huggingface_service import HuggingFaceService
        
        data = request.get_json()
        token = data.get("token")
        repo_id = data.get("repo_id")
        
        if not token or not repo_id:
            return jsonify({"status": "error", "message": "Token and Repo ID are required."}), 400
            
        hf_service = HuggingFaceService()
        result = hf_service.upload_models(token, repo_id)
        
        status_code = 200 if result["status"] == "success" else 500
        return jsonify(result), status_code
        
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500

