# filename: database/db_manager.py
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
import threading

class DatabaseManager:
    """
    SQLite 데이터베이스를 관리하는 클래스.
    - 데이터베이스 연결 (스레드 안전)
    - 테이블 생성
    - CRUD 작업 처리
    """
    _local = threading.local()  # Thread-local storage for connections
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_connection()
        self._create_table()
        print(f"Database initialized and connected at '{self.db_path}'")
    
    def _init_connection(self):
        """Initialize a new connection with proper settings"""
        conn = sqlite3.connect(
            self.db_path, 
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode to reduce locking
            timeout=10.0
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        self._local.conn = conn
        return conn
    
    @property
    def conn(self):
        """Get connection, create new one if needed"""
        try:
            conn = getattr(self._local, 'conn', None)
            if conn is None:
                return self._init_connection()
            # Test connection is alive
            conn.execute("SELECT 1")
            return conn
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            # Connection is closed or broken, create new one
            return self._init_connection()

    def _create_table(self):
        """genetic_records 테이블이 없으면 생성합니다."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genetic_records (
                record_id TEXT PRIMARY KEY,
                dna_sequence TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                death_time TEXT
            )
        """)
        # autocommit mode, no commit needed

    def add_record(self, record_id: str, dna_sequence: str, birth_time: datetime):
        """새로운 유전 기록을 데이터베이스에 추가합니다."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO genetic_records (record_id, dna_sequence, birth_time) VALUES (?, ?, ?)",
            (record_id, dna_sequence, birth_time.isoformat())
        )
        # autocommit mode, no commit needed

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
        # autocommit mode, no commit needed

    def close(self):
        """데이터베이스 연결을 닫습니다."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
