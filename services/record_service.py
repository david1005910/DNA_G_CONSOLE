# filename: services/record_service.py
import uuid
from datetime import datetime
from typing import Optional, List
from database.db_manager import DatabaseManager

# 데이터 모델 역할을 하는 간단한 클래스 정의
class GeneticRecord:
    def __init__(self, record_id: str, dna_sequence: str, birth_time: datetime, death_time: Optional[datetime] = None):
        self.record_id = record_id
        self.dna_sequence = dna_sequence
        self.birth_time = birth_time
        self.death_time = death_time

    def transcribe_to_rna(self) -> str:
        """DNA 서열을 RNA 서열로 변환합니다. (T -> U)"""
        return self.dna_sequence.replace('T', 'U')

    def __repr__(self):
        status = "ALIVE" if self.death_time is None else f"DECEASED"
        return (f"GeneticRecord(ID: {self.record_id[:8]}..., Status: {status}, "
                f"DNA: {self.dna_sequence[:10]}..., "
                f"Born: {self.birth_time.strftime('%Y-%m-%d %H:%M')})")

class RecordService:
    """유전 정보 기록과 관련된 비즈니스 로직을 처리하는 서비스 클래스."""
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create_record(self, dna_sequence: str) -> Optional[GeneticRecord]:
        """새로운 유전 정보 기록을 생성하고 데이터베이스에 저장합니다."""
        if not all(base in "ATCG" for base in dna_sequence):
            print(f"Error: Invalid DNA sequence provided.")
            return None
        
        new_record = GeneticRecord(
            record_id=str(uuid.uuid4()),
            dna_sequence=dna_sequence,
            birth_time=datetime.now()
        )
        self.db.add_record(new_record.record_id, new_record.dna_sequence, new_record.birth_time)
        print(f"New record created: {new_record.record_id}")
        return new_record

    def terminate_record(self, record_id: str) -> bool:
        """ID에 해당하는 기록을 '소멸' 상태로 변경합니다."""
        record_data = self.db.get_record(record_id)
        if record_data and record_data[3] is None:  # death_time이 없을 경우
            self.db.update_death_time(record_id, datetime.now())
            print(f"Record {record_id} has been terminated.")
            return True
        elif record_data:
            print(f"Record {record_id} was already terminated.")
            return False
        else:
            print(f"Record with ID {record_id} not found.")
            return False

    def find_record_by_id(self, record_id: str) -> Optional[GeneticRecord]:
        """ID를 사용하여 특정 기록을 조회합니다."""
        record_data = self.db.get_record(record_id)
        if record_data:
            return GeneticRecord(
                record_id=record_data[0],
                dna_sequence=record_data[1],
                birth_time=datetime.fromisoformat(record_data[2]),
                death_time=datetime.fromisoformat(record_data[3]) if record_data[3] else None
            )
        return None

    def list_all_records(self) -> List[GeneticRecord]:
        """모든 기록을 조회하여 객체 리스트로 반환합니다."""
        all_records_data = self.db.get_all_records()
        return [
            GeneticRecord(
                record_id=row[0], dna_sequence=row[1], 
                birth_time=datetime.fromisoformat(row[2]),
                death_time=datetime.fromisoformat(row[3]) if row[3] else None
            ) for row in all_records_data
        ]
