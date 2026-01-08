# 🧪 Sandbox 기능 및 분석 보고서

---

## 1. 제어 패널 버튼 및 백엔드 로직

### 1.1 임베딩 재학습 (Embedding Retraining)

**Frontend**

- Handler: `handleRetrain`

**API**

- `POST /api/ml/retrain`

**Backend Logic**

- `train_model.retrain_model_from_db()` 호출
- 데이터베이스 내 모든 DNA 시퀀스 로드
- Scikit-learn 파이프라인 실행
  - CountVectorizer
  - RandomForestClassifier
- 학습 산출물 저장
  - `ml_models/model.joblib`
  - `ml_models/training_metrics.joblib`
- Flask 애플리케이션 메모리 내
  - `MLService` 인스턴스 갱신

**의미**

- 모델 파라미터 및 성능 지표의 기준점이 변경됨
- 이후 모든 예측 및 인사이트의 **신뢰 기준선**이 재정의됨

---

### 1.2 시퀀스 학습 (Sequence Learning)

**Frontend**

- Handler: `handleSeqTrain`

**API**

- `POST /api/ml/retrain`

**Backend Logic**

- 현재 구현상 임베딩 재학습과 **완전히 동일**
- 모델 전체 재학습 수행

**특이사항**

- UI 상 개념적으로 분리되어 있으나
- 기술적으로는 동일한 학습 파이프라인을 공유

**권장 개선**

- 향후:
  - Incremental learning
  - Sequence-only feature 학습
  등으로 분리 가능

---

### 1.3 메타 분석 (Meta Analysis)

**Frontend**

- Handler: `handleMetaTrain`

**API**

- `POST /api/analysis/virus-identity`

**Backend Logic**

- 중복 출현 시퀀스 그룹 식별
  - `occurrence_count > 1`
- `source_metadata` 필드 파싱
  - JSON / String 혼합 처리
- 다음 기준으로 통계 집계
  - Virus Type
  - Host
  - Location
  - Year
- 결과는 JSON 형태로 즉시 반환
- 별도 DB 저장 없음 (Stateless)

**의미**

- 모델과 무관한 **순수 데이터 관측 계층**
- 수집 데이터의 구조적 편향/분포를 확인하는 용도

---

### 1.4 바이러스 동일성 분석 (Label / Group)

**UI 구조**

- 단일 버튼 ❌
- `시퀀스 학습` + `메타 분석` 버튼을 포함하는 그룹 개념

**실질 기능**

- 동일 DNA 시퀀스 기반 그룹화
- 메타데이터 통계 집계

**정의**

- 독립 기능이라기보다는
- **메타 분석의 의미적 상위 개념**

---

## 2. 분석 패널별 영향 분석 (Impact Analysis)

---

### 2.1 Engine Analysis (엔진 분석)

**주요 API**

- `GET /api/ml/inspect`

**영향을 주는 버튼**

- 임베딩 재학습
- 시퀀스 학습

**변화 내용**
