import os
import random
import joblib
import numpy as np
import math
from typing import List, Tuple, Dict
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from dna_app.database.db_manager import DatabaseManager
from dna_app.services.feature_extractor import BiologicalFeatureExtractor
from config import config



# --- 2. Initial Model Training (Synthetic) ---
def generate_synthetic_dna(
    length: int, 
    bias_type: str, 
    gc_mean: float = None,
    gc_std: float = 0.05,
    motif: str = None,
    motif_count: int = 3,
    noise_level: float = 0.05
) -> str:
    """
    고도화된 DNA 시퀀스 생성기
    
    Args:
        length: 시퀀스 길이
        bias_type: "HighGC" 또는 "LowGC"
        gc_mean: GC 함량 평균 (None이면 bias_type에 따라 자동 설정)
        gc_std: GC 함량 표준편차 (가우시안 분포용)
        motif: 주입할 히든 모티프 (예: "GCG", "AAAA")
        motif_count: 모티프 주입 횟수
        noise_level: 돌연변이 확률 (0.0 ~ 1.0)
    """
    # 1. 가우시안 분포 기반 GC 함량 결정
    if gc_mean is None:
        gc_mean = 0.65 if bias_type == "HighGC" else 0.35
    
    # 정규분포에서 샘플링, 0.2~0.8 범위로 클리핑
    target_gc = np.clip(np.random.normal(gc_mean, gc_std), 0.2, 0.8)
    
    # GC 비율에 맞게 가중치 계산
    gc_weight = target_gc / 2
    at_weight = (1 - target_gc) / 2
    
    bases = ['G', 'C', 'A', 'T']
    weights = [gc_weight, gc_weight, at_weight, at_weight]
    
    sequence = list("".join(random.choices(bases, weights=weights, k=length)))
    
    # 2. 히든 모티프 주입 (모티프가 지정된 경우)
    if motif:
        motif_len = len(motif)
        for _ in range(motif_count):
            # 랜덤 위치에 모티프 삽입
            pos = random.randint(0, length - motif_len - 1)
            for i, base in enumerate(motif):
                sequence[pos + i] = base
    
    # 3. 노이즈(돌연변이) 주입
    if noise_level > 0:
        for i in range(len(sequence)):
            if random.random() < noise_level:
                sequence[i] = random.choice(['A', 'T', 'G', 'C'])
    
    return "".join(sequence)

def create_synthetic_dataset(num_samples: int):
    """
    개선된 합성 데이터셋 생성 (Edge Case 강화 버전 v2)
    - Type A (HighGC): GC 평균 52%, 'GCG' 모티프 주입
    - Type B (LowGC): GC 평균 48%, 'AAT' 모티프 주입
    - 분포가 크게 겹침 → 모티프가 핵심 분류 기준이 됨
    - 노이즈 10% → 일부 모티프 손상
    """
    sequences = []
    
    # Type A: Slightly High GC + GCG 모티프
    for _ in range(num_samples // 2):
        seq = generate_synthetic_dna(
            length=300, 
            bias_type="HighGC",
            gc_mean=0.52,
            gc_std=0.10,
            motif="GCG",
            motif_count=6,
            noise_level=0.10
        )
        sequences.append(seq)
    
    # Type B: Slightly Low GC + AAT 모티프 (다른 시그니처)
    for _ in range(num_samples // 2):
        seq = generate_synthetic_dna(
            length=300, 
            bias_type="LowGC",
            gc_mean=0.48,
            gc_std=0.10,
            motif="AAT",  # Type B 전용 모티프
            motif_count=6,
            noise_level=0.10
        )
        sequences.append(seq)
        
    random.shuffle(sequences)
    return sequences, None

def train_initial_model(model_path: str):
    print("[Trainer] Starting INITIAL model training (Synthetic + Biologically Enhanced)...")
    X, _ = create_synthetic_dataset(num_samples=200)
    
    # 합성 데이터에서도 동일한 로직으로 학습
    return _train_and_save(X, model_path)


# --- 3. DB Retraining ---
def retrain_model_from_db(model_path: str, db_path: str):
    print("[Trainer] Starting model RETRAINING from database...")
    db_manager = DatabaseManager(db_path)
    records = db_manager.get_all_records()
    db_manager.close()

    if len(records) < 10: 
        msg = f"[Trainer] Not enough data. Found {len(records)} records."
        print(msg)
        return False, msg

    # Schema: id(0), seq(1), ... count(5)
    sequences = [row[1] for row in records]
    
    # Weights extraction
    weights = []
    for row in records:
        w = 1
        if len(row) > 5 and row[5] is not None:
             try: w = int(row[5])
             except: w = 1
        weights.append(w)
    
    return _train_and_save(sequences, model_path, weights)


# --- 4. Common Training Logic ---
def _train_and_save(X: List[str], model_path: str, weights: List[int] = None) -> Tuple[bool, str]:
    if not X: return False, "No data."
    if weights is None: weights = [1] * len(X)
    
    # 1. Feature Extraction First (to generate labels)
    print("[Trainer] Extracting biological features for profiling...")
    extractor = BiologicalFeatureExtractor(kmer_size=3)
    X_features = extractor.transform(X)
    
    # 2. Unsupervised Labeling (K-Means)
    # 생물학적 특징을 기반으로 자연스러운 2개 군집(Type A/B)을 발견
    print("[Trainer] Inferring latent labels using K-Means clustering...")
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_features)
    
    # Cluster 0 -> Type A, Cluster 1 -> Type B (Mapping might vary, but consistency is key)
    # To make it somewhat consistent, let's say High GC content cluster is always 'Type A'
    # Calculate AVG GC content for cluster 0
    gc_indices = [0] # 0th feature is GC content
    cluster_0_indices = [i for i, c in enumerate(clusters) if c == 0]
    if cluster_0_indices:
        avg_gc_0 = np.mean([X_features[i][0] for i in cluster_0_indices])
    else:
        avg_gc_0 = 0
        
    # If Cluster 0 is High GC, map 0->Type A. Else 0->Type B.
    # We define Type A as the "High GC / Structured" type based on prompt context
    avg_gc_global = np.mean([f[0] for f in X_features])
    
    if avg_gc_0 > avg_gc_global:
        label_map = {0: "Type A", 1: "Type B"}
    else:
        label_map = {0: "Type B", 1: "Type A"}
        
    y_labels = [label_map[c] for c in clusters]
    
    # 4. 라벨 노이즈 추가 (현실적인 오분류 유도, 10% 확률)
    import random as rnd
    rnd.seed(42)
    for i in range(len(y_labels)):
        if rnd.random() < 0.10:  # 10% 확률로 라벨 뒤집기
            y_labels[i] = "Type B" if y_labels[i] == "Type A" else "Type A"
    
    print(f"[Trainer] Inferred Labels Distribution (after noise): {Counter(y_labels)}")

    # 5. Supervised Training (RandomForest with reduced complexity)
    # 트리 수를 줄여 약간의 오분류가 발생하도록 유도
    
    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        X, y_labels, weights, test_size=0.2, random_state=42, stratify=y_labels
    )
    
    pipeline = Pipeline([
        ('bio_features', BiologicalFeatureExtractor(kmer_size=3)),
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train, classifier__sample_weight=w_train)
    
    # Extract raw components for portability
    classifier = pipeline.named_steps['classifier']
    scaler = pipeline.named_steps['scaler']
    extractor_obj = pipeline.named_steps['bio_features']
    
    y_pred = pipeline.predict(X_test)
    print("\n[Trainer] Evaluation on Test Split:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Calculate and save training metrics for frontend visualization
    from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
    
    cm = confusion_matrix(y_test, y_pred, labels=["Type A", "Type B"])
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, pos_label="Type A", zero_division=0)
    precision = precision_score(y_test, y_pred, pos_label="Type A", zero_division=0)
    recall = recall_score(y_test, y_pred, pos_label="Type A", zero_division=0)
    
    # Get class probabilities for confidence distribution
    y_proba = pipeline.predict_proba(X_test)
    confidence_scores = [max(p) for p in y_proba]
    
    training_metrics = {
        "confusion_matrix": cm.tolist(),
        "labels": ["Type A", "Type B"],
        "accuracy": float(accuracy),
        "f1_score": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "test_size": len(y_test),
        "train_size": len(y_train),
        "confidence_distribution": {
            "high": sum(1 for c in confidence_scores if c >= 0.8),
            "medium": sum(1 for c in confidence_scores if 0.5 <= c < 0.8),
            "low": sum(1 for c in confidence_scores if c < 0.5)
        }
    }
    
    # Save
    model_dir = os.path.dirname(model_path)
    os.makedirs(model_dir, exist_ok=True)
    
    # HF Portability: Save components separately
    # Note: We save the classifier under the same name but it's now just the classifier
    joblib.dump(classifier, model_path)
    joblib.dump(scaler, os.path.join(model_dir, "scaler_rf.joblib"))
    # (Optional) Save extractor if needed, but we provide code in inference.py
    
    print(f"[Trainer] Raw Model saved to {model_path}")
    
    # Save Feature Names for XAI
    feature_names = extractor_obj.get_feature_names_out().tolist()
    fn_path = os.path.join(model_dir, "feature_names.joblib")
    joblib.dump(feature_names, fn_path)
    print(f"[Trainer] Feature names saved to {fn_path}")
    
    # Save Training Metrics
    metrics_path = os.path.join(model_dir, "training_metrics.joblib")
    joblib.dump(training_metrics, metrics_path)
    print(f"[Trainer] Training metrics saved to {metrics_path}")
    
    return True, "Model retrained with biological enhancements."


# --- 5. Sequence-Specific Training (NEW) ---
def train_sequence_model(model_path: str, db_path: str):
    """
    시퀀스 고유 특징 학습 - 메타데이터 기반 지도 학습
    기존 임베딩 재학습과 분리된 독립 모델
    """
    from sklearn.ensemble import GradientBoostingClassifier
    from dna_app.services.sequence_feature_extractor import SequenceFeatureExtractor
    import json
    import re
    
    print("[SequenceTrainer] Starting SEQUENCE-SPECIFIC model training...")
    
    db_manager = DatabaseManager(db_path)
    conn = db_manager.conn
    cursor = conn.cursor()
    
    # 메타데이터가 있는 레코드만 가져오기
    cursor.execute("""
        SELECT dna_sequence, source_metadata 
        FROM genetic_records 
        WHERE source_metadata IS NOT NULL AND source_metadata != '[]'
    """)
    records = cursor.fetchall()
    db_manager.close()
    
    if len(records) < 20:
        msg = f"[SequenceTrainer] Not enough labeled data. Found {len(records)} records."
        print(msg)
        return False, msg
    
    # 메타데이터에서 바이러스 타입 추출하여 라벨 생성
    sequences = []
    labels = []
    
    for seq, meta_str in records:
        if not seq or not meta_str:
            continue
        
        # 메타데이터 파싱
        virus_type = None
        try:
            if isinstance(meta_str, str):
                # JSON 또는 단순 문자열
                if 'Influenza A' in meta_str:
                    virus_type = 'Influenza A'
                elif 'Influenza B' in meta_str:
                    virus_type = 'Influenza B'
                elif 'Norovirus' in meta_str:
                    virus_type = 'Norovirus'
                elif 'Chicken anemia' in meta_str:
                    virus_type = 'Chicken anemia virus'
                else:
                    # 기타 바이러스 또는 알 수 없음
                    virus_type = 'Other'
        except:
            continue
        
        if virus_type:
            sequences.append(seq)
            labels.append(virus_type)
    
    if len(sequences) < 20:
        msg = f"[SequenceTrainer] Not enough parsed labels. Found {len(sequences)} valid samples."
        print(msg)
        return False, msg
    
    # 희귀 클래스 필터링 (최소 10개 샘플 필요 - 과적합 방지)
    label_counts = Counter(labels)
    valid_labels = {label for label, count in label_counts.items() if count >= 10}
    
    if len(valid_labels) < 2:
        msg = f"[SequenceTrainer] Not enough distinct classes. Need at least 2 classes with 10+ samples each."
        print(msg)
        return False, msg
    
    # 유효한 라벨만 필터링
    filtered_data = [(seq, label) for seq, label in zip(sequences, labels) if label in valid_labels]
    sequences = [d[0] for d in filtered_data]
    labels = [d[1] for d in filtered_data]
    
    print(f"[SequenceTrainer] Parsed {len(sequences)} sequences with labels: {Counter(labels)}")
    
    # Feature Extraction
    extractor = SequenceFeatureExtractor(kmer_size=5)
    X_features = extractor.transform(sequences)
    
    # Train/Test Split (희귀 클래스 제거 후 stratify 안전하게 사용)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, labels, test_size=0.2, random_state=42, stratify=labels
        )
    except ValueError:
        # stratify 실패 시 일반 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, labels, test_size=0.2, random_state=42
        )
    
    # 클래스 가중치 계산 (역빈도 가중치로 클래스 불균형 보정)
    from sklearn.utils.class_weight import compute_class_weight
    unique_classes = np.unique(y_train)
    class_weights = compute_class_weight('balanced', classes=unique_classes, y=y_train)
    class_weight_dict = dict(zip(unique_classes, class_weights))
    
    # 샘플별 가중치 생성
    sample_weights = np.array([class_weight_dict[label] for label in y_train])
    
    print(f"[SequenceTrainer] Class weights applied: {class_weight_dict}")
    
    # GradientBoosting 학습 (클래스 가중치 적용)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', GradientBoostingClassifier(
            n_estimators=100, 
            max_depth=3,  # 감소: 과적합 방지
            learning_rate=0.05,  # 감소: 더 안정적인 학습
            min_samples_leaf=10,  # 추가: 리프 노드 최소 샘플
            random_state=42
        ))
    ])
    
    pipeline.fit(X_train, y_train, classifier__sample_weight=sample_weights)
    
    # Extract raw components for portability
    classifier = pipeline.named_steps['classifier']
    scaler = pipeline.named_steps['scaler']
    
    y_pred = pipeline.predict(X_test)
    print("\n[SequenceTrainer] Evaluation on Test Split:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Metrics 계산
    from sklearn.metrics import accuracy_score, f1_score
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    training_metrics = {
        "accuracy": float(accuracy),
        "f1_score": float(f1),
        "labels": list(set(labels)),
        "train_size": len(y_train),
        "test_size": len(y_test),
        "label_distribution": dict(Counter(labels)),
        "model_type": "GradientBoostingClassifier",
        "feature_count": X_features.shape[1],
        "trained_at": __import__('datetime').datetime.now().isoformat()
    }
    
    # 저장
    model_dir = os.path.dirname(model_path)
    sequence_model_path = os.path.join(model_dir, "sequence_model.joblib")
    sequence_metrics_path = os.path.join(model_dir, "sequence_metrics.joblib")
    sequence_scaler_path = os.path.join(model_dir, "scaler_gb.joblib") # New
    
    # HF Portability: Save components separately
    joblib.dump(classifier, sequence_model_path)
    joblib.dump(scaler, sequence_scaler_path)
    joblib.dump(training_metrics, sequence_metrics_path)
    # joblib.dump(extractor, sequence_extractor_path) # Extractor logic will be in inference.py
    
    print(f"[SequenceTrainer] Sequence model saved to {sequence_model_path}")
    print(f"[SequenceTrainer] Metrics saved to {sequence_metrics_path}")
    
    return True, f"Sequence model trained. Accuracy: {accuracy*100:.1f}%, F1: {f1*100:.1f}%"


if __name__ == '__main__':
    config.setup_directories()
    train_initial_model(config.MODEL_FILE)

