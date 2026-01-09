# DNA Sequence Classifier & Management System (TEST)

(DNA 서열 분류 및 관리 시스템)

This project is a sandbox implementation of an AI-powered DNA sequence classifier. It uses Machine Learning (Random Forest) to classify DNA sequences into "Type A" or "Type B" based on genetic motifs (specifically 'GCG' patterns), and provides a system to manage these records.

## ✨ New: Single Web Interface (통합 관리자 인터페이스)

이제 복잡한 명령어 없이 **웹 페이지 하나에서 모든 것을 관리**할 수 있습니다.
👉 **접속 URL**: `http://localhost:5001/`

### 🖥️ Dashboard Features (대시보드 기능)

1. **📖 README 탭**: 프로젝트 설명서와 가이드를 바로 확인
2. **🧬 Records 탭**:
   - **생성**: DNA 서열 입력 → AI 실시간 분석(Type A/B 예측) → DB 저장
   - **조회**: 전체 기록 목록 및 상세 정보 열람
   - **관리**: 기록 소멸(Terminate) 처리
3. **🔬 API Tester 탭**: Postman/Curl 없이 UI에서 직접 REST API 테스트
4. **⚙️ System 탭**:
   - 시스템 상태 모니터링 (DB 연결, 모델 로드 상태)
   - 문제 해결 가이드 제공

---

## 🚀 One-Click Run (실행 방법)

### Option 1: Local Python (로컬 실행)

모델이 없으면 **자동으로 학습**하고 서버를 시작합니다.

```bash
# 1. 의존성 설치 (최초 1회)
pip install -r requirements.txt

# 2. 서버 실행
python run.py
```

*실행 후 브라우저에서 `http://localhost:5001` 접속*

### Option 2: Docker (도커 실행)

환경 설정 걱정 없이 컨테이너로 실행합니다.

```bash
docker-compose up --build
```

---

## 📂 Project Structure (프로젝트 구조)

- **`main.py`**: (데모용) CLI에서 학습부터 예측까지 전체 시나리오 자동 시연
- **`run.py`**: **[Main Entry]** API 서버 및 React Admin UI 실행 (자동 모델 학습 포함)
- **`public/`**: React 프론트엔드 소스 (Admin UI)
- **`dna_app/`**: Flask 백엔드 (API, DB, AI 서비스)
- **`ml_models/`**: AI 모델 파일 저장소
- **`database/`**: SQLite 데이터베이스 저장소

## 🛠️ API Reference

웹 UI 대신 직접 API를 호출할 수도 있습니다.

- **POST `/api/records`**: `{ "dna_sequence": "..." }` → 기록 생성 및 예측
- **GET `/api/records`**: 모든 기록 조회
- **PUT `/api/records/<id>/terminate`**: 기록 소멸 처리
- **GET `/api/readme`**: 문서 내용 반환
- **GET `/api/system/status`**: 시스템 상태 반환

## 🧠 AI Model Logic

- **Algorithm**: Random Forest Classifier
- **Features**: 3-gram character counting
- **Logic**:
  - **Type A**: Contains "GCG" motifs (High immunity potential)
  - **Type B**: Random sequence (Noise)
