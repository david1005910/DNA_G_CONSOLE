import requests
import uuid
from datetime import datetime
from typing import List, Dict
import sqlite3
import os

class RecordService:
    def __init__(self, db_manager=None, db_file=None):
        if db_manager:
            self.db_file = db_manager.db_path
            self.db_manager = db_manager
        else:
            self.db_file = db_file
            self.db_manager = None

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def get_ncbi_meta(self, record_type='DNA') -> Dict:
        """NCBI에서 현재 조건에 맞는 전체 데이터 개수를 조회합니다."""
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        # Query based on type
        term = "Viruses[Organism] AND 200:1000[SLEN] AND biomol_genomic[PROP]"
        if record_type == 'RNA':
            term = "Viruses[Organism] AND 200:1000[SLEN] AND biomol_mrna[PROP]"
            
        search_params = {
            "db": "nucleotide",
            "term": term,
            "retmode": "json",
            "retmax": 0
        }
        try:
            resp = requests.get(search_url, params=search_params, timeout=10)
            data = resp.json()
            return {"total_count": int(data.get("esearchresult", {}).get("count", 0))}
        except Exception as e:
            print(f"NCBI Meta Error: {e}")
            return {"total_count": 5000}

    def fetch_real_samples_from_ncbi(self, count=20, record_type='DNA', sort='relevance') -> List[str]:
        print(f"[RecordService] Fetching {count} real viral {record_type} samples from NCBI... (Sort: {sort})")
        
        # Load Offset from DB
        start_ret = 0
        offset_key = f"ncbi_offset_{record_type}"
        
        # If sorting by date, we might not want to use the same offset logic as relevance, 
        # but for simplicity, we'll keep it or reset it if needed. 
        # Actually, for 'date', offset works to get older records if we paginate.
        
        if self.db_manager:
            val = self.db_manager.get_metadata(offset_key)
            if val: start_ret = int(val)
        else:
            # Fallback direct query
            try:
                conn = self.get_db_connection()
                curs = conn.cursor()
                curs.execute("SELECT value FROM system_metadata WHERE key = ?", (offset_key,))
                row = curs.fetchone()
                if row: start_ret = int(row[0])
                conn.close()
            except: pass

        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        term = "Viruses[Organism] AND 200:1000[SLEN] AND biomol_genomic[PROP]"
        if record_type == 'RNA':
            term = "Viruses[Organism] AND 200:1000[SLEN] AND biomol_mrna[PROP]"
            
        # Map sort param to NCBI values
        # 'relevance' -> 'relevance'
        # 'date' -> 'pdat' (Publication Date) or 'date' depending on EUtils version, strictly 'date' is often used for Entrez.
        ncbi_sort = 'relevance'
        if sort == 'date':
            ncbi_sort = 'date' # Sort by publication date (newest first)

        search_params = {
            "db": "nucleotide",
            "term": term,
            "retmode": "json",
            "retmax": count,
            "retstart": start_ret,
            "sort": ncbi_sort
        }
        
        id_list = []
        try:
            resp = requests.get(search_url, params=search_params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"Search Error: {e}")
            return []

        if not id_list:
            return []

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "nucleotide",
            "id": ",".join(id_list),
            "rettype": "fasta",
            "retmode": "text"
        }

        created_ids = []
        try:
            resp = requests.get(fetch_url, params=fetch_params, timeout=20)
            resp.raise_for_status()
            fasta_data = resp.text
            
            parsed_records = []
            current_header = ""
            current_seq = []
            
            for line in fasta_data.split('\n'):
                if line.startswith('>'):
                    if current_header:
                        parsed_records.append({'header': current_header, 'seq': "".join(current_seq)})
                    current_header = line[1:].strip()
                    current_seq = []
                else:
                    current_seq.append(line.strip())
            
            if current_header:
                parsed_records.append({'header': current_header, 'seq': "".join(current_seq)})

            if self.db_manager:
                for rec in parsed_records[:count]:
                    seq = rec['seq']
                    header = rec['header']
                    
                    if len(seq) < 100: continue

                    # Upsert (Deduplication handled in DB)
                    rid = str(uuid.uuid4())
                    self.db_manager.upsert_record(rid, seq, datetime.now(), record_type, source_info=header)
                    created_ids.append(rid)
            else:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT record_type FROM genetic_records LIMIT 1")
                except:
                     cursor.execute("ALTER TABLE genetic_records ADD COLUMN record_type TEXT DEFAULT 'DNA'")
                
                for seq in sequences[:count]:
                    if len(seq) < 100: continue
                    # Check Duplicates
                    cursor.execute("SELECT 1 FROM genetic_records WHERE dna_sequence = ? LIMIT 1", (seq,))
                    if cursor.fetchone():
                        print("[RecordService] Duplicate sequence skipped.")
                        continue

                    rid = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO genetic_records (record_id, dna_sequence, birth_time, record_type) VALUES (?, ?, ?, ?)",
                        (rid, seq, datetime.now().isoformat(), record_type)
                    )
                    created_ids.append(rid)
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Fetch Error: {e}")

        # Save Offset to DB
        new_offset = start_ret + count
        if self.db_manager:
            self.db_manager.set_metadata(offset_key, str(new_offset))
        else:
            try:
                conn = self.get_db_connection()
                curs = conn.cursor()
                curs.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES (?, ?)", (offset_key, str(new_offset)))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Offset Save Error: {e}")

        return created_ids
