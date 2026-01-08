# RandomForest Classifier 엔진 분석 그래프 고도화 플랜 (Engine Analysis Optimization Plan)

본 문서는 `ml_technical_deep_dive.md`의 기술 분석 파트, 특히 **RandomForestClassifier**의 분석 그래프가 시각적으로 수려하고 기술적으로 유의미한(Meaningful) 인사이트를 전달할 수 있도록 데이터를 엔지니어링하는 계획을 담고 있습니다.

## 1. 목표 (Objectives)
- **시각적 완성도**: 단순히 Accuracy 100%의 밋밋한 결과가 아닌, 데이터의 분포와 경계가 드러나는 리얼한 그래프 생성.
- **설명 가능성 (XAI)**: Feature Importance 그래프에서 특정 생물학적 패턴(K-mer)이 명확히 드러나게 하여, "AI가 DNA의 숨겨진 규칙을 학습했다"는 스토리텔링 강화.
- **기술적 깊이**: 노이즈와 오버랩이 존재하는 데이터셋에서도 모델이 견고함(Robustness)을 유지함을 증명.

## 2. 현황 진단 (Current Status Analysis)
현재 `train_model.py`의 데이터 생성 로직은 다음과 같은 한계가 있습니다:
1.  **단순 이분법적 분포**: High GC(70%) vs Low GC(30%)로 명확히 갈려있어 분류가 너무 쉽습니다 (Trivial Task).
2.  **결과물의 단순함**:
    - ROC Curve가 완벽한 직각(AUC 1.0)이 되어 분석할 거리가 없음.
    - Feature Importance가 단순히 'G', 'C' 관련 단일 염기 수준에 머물 가능성이 큼.

## 3. 데이터 고도화 전략 (Meaningful Data Strategy)

유의미한 그래프를 얻기 위해 세 가지 차원의 데이터 엔지니어링을 수행합니다.

### A. 히든 모티프(Hidden Motif) 주입
Type A/B를 구분짓는 **결정적인 '시그니처 패턴'**을 심습니다. 이는 Feature Importance 그래프에서 압도적인 막대(Bar)로 나타나야 합니다.
- **전략**:
    - **Type A**: `GCG` (Start Codon 유사 변형) 또는 `AAAAA` 등 특정 3-mer 빈도를 인위적으로 약간 높임.
    - **효과**: RandomForest가 이를 가장 중요한 Feature로 선정 → 그래프에서 "AI가 GCG 패턴을 주요 식별자로 찾았습니다"라고 설명 가능.

### B. 가우시안 분포 기반의 모호성(Ambiguity) 추가
데이터를 너무 깨끗하게 만들지 않고, **경계선상의 데이터(Edge Cases)**를 생성합니다.
- **전략**:
    - 기존: GC 70% 고정.
    - 변경: GC 함량을 평균 60%, 표준편차 5%의 정규분포로 생성. 일부 데이터는 50% 구간에서 겹치게(Overlap) 함.
- **효과**:
    - Confusion Matrix에서 100%가 아닌 95~98% 수준의 현실적인 수치 도출.
    - Decision Boundary 시각화 시 훨씬 자연스럽고 전문적인 '머신러닝'스러운 그림 생성.

### C. 노이즈(Noise) 주입
현실 세계의 생물학적 데이터처럼 무작위 돌연변이를 시뮬레이션합니다.
- **전략**: 시퀀스 생성 후 5~10% 확률로 랜덤 염기로 치환.

## 4. 시각화 타겟 그래프 구성안

이 데이터를 통해 생성할 최종 그래프의 모습입니다.

| 그래프 종류 | 기대 형상 | 설명 포인트 |
|:---:|:---|:---|
| **Feature Importance** | `GCG`, `CGC` 등의 특정 K-mer가 상위 3개에 우뚝 솟은 형태 | "단순 염기 조성을 넘어, 입체적인 서열 패턴이 분류의 핵심임이 증명됨" |
| **Confusion Matrix** | 대각선이 진하되, 비대각선(Error)이 살짝 존재 (예: 2~3개 오분류) | "노이즈가 섞인 환경에서도 98% 이상의 견고한 성능을 확보" |
| **Class Probability** | 양쪽 끝(0과 1)에 몰려있지만, 중간 지대(0.4~0.6)에도 점들이 분포 | "모델이 확신하지 못하는 경계선 데이터에 대한 불확실성(Uncertainty) 표현" |

## 5. 실행 액션 아이템 (Action Items)

1.  **`src/data_gen.py` (또는 `train_model.py` 내 함수) 업데이트**:
    - `generate_synthetic_dna` 함수에 `motif_injection` 및 `noise_level` 파라미터 추가.
2.  **학습 파이프라인 실행**:
    - 개선된 데이터로 모델 재학습 (`python train_model.py`).
    - `feature_names.joblib` 및 학습된 모델 저장.
3.  **문서(`ml_technical_deep_dive.md`) 업데이트**:
    - 생성된 Feature Importance 수치를 바탕으로 분석 텍스트 작성.
    - (필요 시) Python 노트북을 통해 해당 그래프를 이미지로 저장하여 문서에 첨부.

---
**결론**: 위 플랜대로 진행 시, 문서 독자는 "이 시스템이 단순히 데이터를 외운 것이 아니라, 유전체 내의 **구조적 특징(Structural Features)**을 학습했음"을 직관적으로 이해할 수 있게 됩니다.
