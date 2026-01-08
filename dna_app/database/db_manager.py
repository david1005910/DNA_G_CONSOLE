# filename: dna_app/database/db_manager.py
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class DatabaseManager:
    """
    SQLite 데이터베이스를 관리하는 클래스.
    - 데이터베이스 연결
    - 테이블 생성
    - CRUD 작업 처리
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_table()
        print(f"Database initialized and connected at '{self.db_path}'")

    def _create_table(self):
        """genetic_records 테이블이 없으면 생성합니다."""
        cursor = self.conn.cursor()
        # Migration: Check if column exists, if not, recreate or alter (For simplicity in this sandbox, we stick to IF NOT EXISTS)
        # But since we support Factory Reset, the user can just reset.
        # We add 'record_type' column.
        try:
            cursor.execute("SELECT record_type FROM genetic_records LIMIT 1")
        except:
            # Column doesn't exist or table doesn't exist.
            # safe to create if not exists, but we might want to alter if table exists.
            # For this MVP, let's just ensure the CREATE statement has it for new inits.
            pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genetic_records (
                record_id TEXT PRIMARY KEY,
                dna_sequence TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                death_time TEXT,
                record_type TEXT DEFAULT 'DNA'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_genetic_captures (
                capture_id TEXT PRIMARY KEY,
                dna_sequence TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                linked_record_id TEXT,
                source_info TEXT,
                FOREIGN KEY(linked_record_id) REFERENCES genetic_records(record_id)
            )
        """)
        

        # Simple migration for existing tables without the column
        try:
            cursor.execute("ALTER TABLE genetic_records ADD COLUMN record_type TEXT DEFAULT 'DNA'")
        except:
            pass # Already exists

        try:
            cursor.execute("ALTER TABLE genetic_records ADD COLUMN occurrence_count INTEGER DEFAULT 1")
            cursor.execute("ALTER TABLE genetic_records ADD COLUMN source_metadata TEXT DEFAULT '[]'")
        except:
            pass # Already exists
        
        try:
             cursor.execute("SELECT capture_id FROM raw_genetic_captures LIMIT 1")
        except:
             # Create table if migration needed (though usually _create_table handles it)
             pass

        # User Documents Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_documents (
                doc_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                enhanced_content TEXT,
                source_type TEXT DEFAULT 'user',
                source_path TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        try:
            cursor.execute("ALTER TABLE user_documents ADD COLUMN enhanced_content TEXT")
        except:
            pass # Already exists

        self.conn.commit()

    def upsert_record(self, record_id: str, dna_sequence: str, birth_time: datetime, record_type: str = 'DNA', source_info: str = ""):
        """
        유전 기록을 추가하거나 업데이트합니다 (Upsert).
        - raw_genetic_captures 에 무조건 저장 (History)
        - genetic_records 에는 유니크한 시퀀스만 저장 (Unique)
        이미 동일한 시퀀스가 존재하면: 카운트 증가, 메타데이터 추가.
        없으면: 새로 추가.
        """
        import uuid
        import json
        
        cursor = self.conn.cursor()
        
        # Check existing
        cursor.execute("SELECT record_id, occurrence_count, source_metadata FROM genetic_records WHERE dna_sequence = ?", (dna_sequence,))
        existing = cursor.fetchone()
        
        target_record_id = record_id
        
        if existing:
            # Update existing
            orig_id, count, meta_json = existing
            target_record_id = orig_id
            new_count = (count or 1) + 1
            
            # Simple metadata append logic
            try:
                meta = json.loads(meta_json) if meta_json else []
            except:
                meta = []
            
            if source_info:
                meta.append(source_info)
            
            # 최신 50개까지만 유지 (데이터 폭증 방지)
            if len(meta) > 50:
                meta = meta[-50:]
            
            cursor.execute("""
                UPDATE genetic_records 
                SET occurrence_count = ?, source_metadata = ?, birth_time = ? 
                WHERE record_id = ?
            """, (new_count, json.dumps(meta), birth_time.strftime('%Y-%m-%d %H:%M:%S.%f'), orig_id))
        else:
            # Insert new
            meta_list = [source_info] if source_info else []
            cursor.execute("""
                INSERT INTO genetic_records (record_id, dna_sequence, birth_time, record_type, occurrence_count, source_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (record_id, dna_sequence, birth_time.strftime('%Y-%m-%d %H:%M:%S.%f'), record_type, 1, json.dumps(meta_list)))
        
        # Raw Capture 저장 (무조건 - 히스토리 보존)
        capture_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO raw_genetic_captures (capture_id, dna_sequence, captured_at, linked_record_id, source_info) VALUES (?, ?, ?, ?, ?)",
            (capture_id, dna_sequence, datetime.now().isoformat(), target_record_id, source_info)
        )
        
        self.conn.commit()
        return target_record_id, not existing  # (record_id, is_new)

    def check_sequence_exists(self, dna_sequence: str) -> bool:
        """주어진 DNA 시퀀스가 이미 DB에 존재하는지 확인합니다."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM genetic_records WHERE dna_sequence = ? LIMIT 1", (dna_sequence,))
        return cursor.fetchone() is not None

    def get_metadata(self, key: str) -> Optional[str]:
        """메타데이터 값을 가져옵니다."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM system_metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except: return None

    def set_metadata(self, key: str, value: str):
        """메타데이터 값을 설정합니다 (Upsert)."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def get_record(self, record_id: str) -> Optional[Tuple]:
        """ID로 특정 기록을 조회합니다."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM genetic_records WHERE record_id = ?", (record_id,))
        return cursor.fetchone()

    def get_all_records(self) -> List[Tuple]:
        """모든 기록을 조회합니다."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM genetic_records ORDER BY birth_time DESC")
        return cursor.fetchall()
        
    def update_death_time(self, record_id: str, death_time: datetime):
        """특정 기록의 사망 시간을 업데이트합니다."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE genetic_records SET death_time = ? WHERE record_id = ?",
            (death_time.isoformat(), record_id)
        )
        self.conn.commit()

    # ========== Document CRUD Methods ==========
    def create_document(self, doc_id: str, title: str, content: str = '', source_type: str = 'user', source_path: str = None) -> bool:
        """새 문서를 생성합니다."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        try:
            cursor.execute(
                "INSERT INTO user_documents (doc_id, title, content, source_type, source_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (doc_id, title, content, source_type, source_path, now, now)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating document: {e}")
            return False

    def get_document(self, doc_id: str) -> Optional[dict]:
        """문서 ID로 문서를 조회합니다."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM user_documents WHERE doc_id = ?", (doc_id,))
        row = cursor.fetchone()
        if row:
            return {
                'doc_id': row[0], 'title': row[1], 'content': row[2],
                'source_type': row[3], 'source_path': row[4],
                'created_at': row[5], 'updated_at': row[6],
                'enhanced_content': row[7]
            }
        return None

    def get_all_documents(self) -> List[dict]:
        """모든 문서 목록을 조회합니다."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT doc_id, title, source_type, source_path, created_at, updated_at, (enhanced_content IS NOT NULL) as has_enhanced FROM user_documents ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        return [{'doc_id': r[0], 'title': r[1], 'source_type': r[2], 'source_path': r[3], 'created_at': r[4], 'updated_at': r[5], 'has_enhanced': bool(r[6])} for r in rows]

    def update_document(self, doc_id: str, title: str = None, content: str = None, enhanced_content: str = None) -> bool:
        """문서를 수정합니다."""
        cursor = self.conn.cursor()
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if enhanced_content is not None:
            updates.append("enhanced_content = ?")
            params.append(enhanced_content)
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(doc_id)
        
        if updates:
            query = f"UPDATE user_documents SET {', '.join(updates)} WHERE doc_id = ?"
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.rowcount > 0
        return False

    def delete_document(self, doc_id: str) -> bool:
        """문서를 삭제합니다."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user_documents WHERE doc_id = ?", (doc_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """데이터베이스 연결을 닫습니다."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

