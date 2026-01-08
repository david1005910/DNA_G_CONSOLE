# DNA Governance & Neural Analysis Console (DG-NAC)
>
> **Next-Gen Genetic Intelligence Management System**

본 시스템은 단순한 데이터 관리를 넘어, 전 세계 유전체 데이터베이스(NCBI)로부터 실시간으로 유전 정보를 획득하고, AI 모델(Random Forest)을 통해 이를 분석/분류하며, 모델의 내사(Inspection) 및 통제까지 가능한 **통합 유전체 거버넌스 플랫폼**입니다.

---

## 🏗️ System Architecture: The "Golden Triangle"

이 서비스는 세 가지 핵심 축(Axis)을 중심으로 설계되었습니다:

### 1. 전술적 데이터 획득 (Tactical Data Acquisition)

* **NCBI E-Utilities Integration**: 미국 국립생물정보센터(NCBI) 서버와 직접 통신하여 실제 바이러스 유전체 서열을 획득합니다.
* **Live HUD Sync**: 사용자가 메뉴를 탐색하는 중에도 백그라운드에서 실시간 크롤링 상태를 추적하며, 전체 가용 데이터 대비 확보율(%)을 프로그레스 바로 표시합니다.
* **Autonomous Harvesting**: 10~15초 주기로 자동 수집 스레드를 운영하여 지속적인 학습 데이터 셋을 구축합니다.

### 2. 신경망 분석 및 통제 (Neural Analysis & Governance)

* **Adaptive Classifier**: RandomForest 알고리즘을 기반으로 DNA 서열의 패턴(k-mer motif)을 분석하여 Type A/B를 판별합니다.
* **Deep Inspection (X-Ray)**: `.joblib` 모델 바이너리를 실시간 해부하여 AI가 결정에 사용한 상위 20개 핵심 유전 패턴(Motif)과 그 가중치를 시각화합니다.
* **Dynamic Re-training**: 수집된 최신 데이터를 바탕으로 현장에서 즉시 모델을 재학습(Re-bind)하여 분석 정확도를 지속적으로 향상시킵니다.

### 3. 영구 저장소 및 아카이브 (Persistent Archive)

* **Unified Registry**: 수집 및 분석된 모든 DNA 서열을 고유 ID(UUID)와 함께 SQLite 기반 영구 저장소에 기록합니다.
* **Telemetry Records**: 각 서열의 예측 타입, 분석 시점, 신뢰도 등을 아카이브하여 필요 시 언제든 전문을 조회할 수 있습니다.
* **Factory Reset**: 시스템 오염이나 테스트 초기화가 필요한 경우, 원클릭으로 DB 소거 및 모델 초기화를 수행합니다.

---

## 🛠️ Main Modules & Features

| 모듈명 | 주요 기능 | 설명 |
| :--- | :--- | :--- |
| **Control Console** | Manual/Auto Sync, Reset | 시스템 전체 제어 및 백그라운드 수집 관리 |
| **Database Explorer** | SQLite Introspection | 저장된 테이블 구조 및 원본 데이터 실시간 조회 |
| **Neural Inspector** | Model Weight Analysis | 가중치 시각화, 알고리즘 파라미터 및 특징 벡터 분석 |
| **Registry Archive** | Full Telemetry View | 분석된 DNA 레코드의 상세 JSON 데이터 및 서열 조회 |
| **Live HUD** | Real-time Progress Tracking | 전체 데이터 중 수집 완료 비중 실시간 시각화 |

---

## 🧬 Scientific Value

이 시스템은 바이오 데이터 전문가와 AI 엔지니어 사이의 가교 역할을 합니다.
* **전문가**: AI가 단순히 결과만 내놓는 것이 아니라, 어떤 유전 패턴을 중요하게 보고 있는지 '이유'를 시각적으로 확인합니다.
* **엔지니어**: 인프라나 복잡한 스크립트 없이도 관리 콘솔에서 원클릭으로 리트레이닝과 데이터 수집 사이클을 관리합니다.

---

## 🚀 Future Roadmap

- [ ] 서열 정렬(Sequence Alignment) 시각화 뷰어 추가
* [ ] 다중 종(Multi-species) 분류 지원 확대
* [ ] 외부 연구기관 전송을 위한 API Export 기능

---
*Created by Antigravity AI Engine v2.5*
