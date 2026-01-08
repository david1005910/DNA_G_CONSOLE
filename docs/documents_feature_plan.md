# 문서 관리 기능 개선 계획

## 현재 문제점
1.  문서 목록이 `localStorage`에만 저장되어 브라우저/세션 간 유지 안 됨.
2.  `docs/` 폴더의 기존 `.md` 파일들이 진입 시 자동으로 불러와지지 않음.
3.  "새 문서"를 클릭해도 빈 화면만 표시됨 (버튼이 주석 처리되어 있음).
4.  빈 "새 문서" 항목들이 `localStorage`에 누적되어 정리가 안 됨.

---

## 구현 계획

### 1. 데이터베이스 모델 추가
-   **파일**: `dna_app/database/db_manager.py`
-   **테이블**: `user_documents`
    ```sql
    CREATE TABLE IF NOT EXISTS user_documents (
        doc_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        source_type TEXT DEFAULT 'user',  -- 'user' | 'system' (docs 폴더)
        source_path TEXT,                  -- 파일 경로 (system 문서용)
        created_at TEXT,
        updated_at TEXT
    );
    ```

---

### 2. API 엔드포인트 추가
-   **파일**: `dna_app/api/docs.py`

| 메서드 | 경로 | 설명 |
|:---|:---|:---|
| `GET` | `/api/docs/list` | 모든 문서 목록 조회 (DB + docs 폴더) |
| `GET` | `/api/docs/<doc_id>` | 특정 문서 내용 조회 |
| `POST` | `/api/docs` | 새 문서 생성 (DB 저장) |
| `PUT` | `/api/docs/<doc_id>` | 문서 수정 |
| `DELETE` | `/api/docs/<doc_id>` | 문서 삭제 |
| `POST` | `/api/docs/load-from-folder` | `docs/` 폴더 파일 DB로 동기화 |

---

### 3. 프론트엔드 수정
-   **파일**: `public/index.html` (`useDocuments` 훅 및 `DocumentsPanel`)

#### 3.1. 초기 로딩
-   컴포넌트 마운트 시 `/api/docs/list` 호출하여 문서 목록 로드.
-   `docs/` 폴더의 시스템 문서와 사용자 생성 문서를 구분하여 표시.

#### 3.2. CRUD 연동
-   `createDocument()`: `POST /api/docs` 호출 → DB 저장.
-   `updateDocument()`: `PUT /api/docs/:id` 호출 → DB 업데이트.
-   `deleteDocument()`: `DELETE /api/docs/:id` 호출 → DB 삭제.
-   `localStorage` 의존성 제거.

#### 3.3. UI 개선
-   "새 문서" 버튼 주석 해제 및 활성화.
-   빈 문서 자동 정리 로직 추가 (제목/내용 없는 문서 필터링).
-   Markdown 렌더링은 `marked.js` 라이브러리 활용 (이미 로드됨).

---

### 4. 시작 시 docs 폴더 동기화
-   서버 시작 시 또는 `/api/docs/load-from-folder` 호출 시:
    -   `docs/*.md` 파일 스캔.
    -   DB에 `source_type='system'`으로 삽입 (중복 시 업데이트).

---

## 예상 작업 순서
1.  `db_manager.py`에 `user_documents` 테이블 생성 로직 추가.
2.  `docs.py` API 엔드포인트 확장.
3.  `index.html`의 `useDocuments` 훅을 API 연동으로 전환.
4.  `DocumentsPanel` UI에서 "새 문서" 버튼 활성화 및 삭제 기능 연결.
5.  진입 시 자동 로딩 및 빈 문서 정리 로직 구현.
