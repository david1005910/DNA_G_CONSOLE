from flask import Blueprint, request, jsonify, current_app
import json
import re

analysis_bp = Blueprint('analysis', __name__)

def parse_metadata(metadata_input):
    """Parse source_metadata JSON and extract structured virus info."""
    # Handle different input types
    if metadata_input is None:
        return []
    
    if isinstance(metadata_input, list):
        meta_list = metadata_input
    elif isinstance(metadata_input, dict):
        meta_list = [str(metadata_input)]
    elif isinstance(metadata_input, str):
        try:
            meta_list = json.loads(metadata_input)
            if not isinstance(meta_list, list):
                meta_list = [str(meta_list)]
        except:
            meta_list = [metadata_input]
    else:
        meta_list = [str(metadata_input)]
    
    parsed = []
    for entry in meta_list:
        if not entry:
            continue
        # Ensure entry is a string for regex operations
        entry_str = str(entry) if not isinstance(entry, str) else entry
        info = {
            'accession': None,
            'virus_type': None,
            'subtype': None,
            'host': None,
            'location': None,
            'year': None,
            'gene': None
        }
        
        # Extract accession ID (e.g., PX795148.1)
        acc_match = re.match(r'^([A-Z]{2}\d+\.\d+)', entry_str)
        if acc_match:
            info['accession'] = acc_match.group(1)
        
        # Extract virus type (expanded list)
        if 'Influenza A' in entry_str:
            info['virus_type'] = 'Influenza A'
            # Extract subtype (H9N2, H3N2, etc.)
            subtype_match = re.search(r'\((H\d+N\d+)\)', entry_str)
            if subtype_match:
                info['subtype'] = subtype_match.group(1)
        elif 'Influenza B' in entry_str:
            info['virus_type'] = 'Influenza B'
        elif 'Norovirus' in entry_str:
            info['virus_type'] = 'Norovirus'
            if 'GII' in entry_str:
                info['subtype'] = 'GII'
            elif 'GI' in entry_str:
                info['subtype'] = 'GI'
        elif 'Dengue virus' in entry_str:
            info['virus_type'] = 'Dengue'
            # Extract type (1-4)
            dengue_match = re.search(r'Dengue virus type (\d)', entry_str)
            if dengue_match:
                info['subtype'] = f'Type {dengue_match.group(1)}'
        elif 'Zika virus' in entry_str:
            info['virus_type'] = 'Zika'
        elif 'Chikungunya' in entry_str:
            info['virus_type'] = 'Chikungunya'
        elif 'West Nile virus' in entry_str:
            info['virus_type'] = 'West Nile'
        elif 'Yellow fever' in entry_str:
            info['virus_type'] = 'Yellow Fever'
        elif 'Hepatitis' in entry_str:
            info['virus_type'] = 'Hepatitis'
            hep_match = re.search(r'Hepatitis ([A-E])', entry_str)
            if hep_match:
                info['subtype'] = hep_match.group(1)
        elif 'COVID' in entry_str or 'SARS-CoV' in entry_str or 'coronavirus' in entry_str.lower():
            info['virus_type'] = 'Coronavirus'
        elif 'RSV' in entry_str or 'Respiratory syncytial' in entry_str:
            info['virus_type'] = 'RSV'
        elif 'Rotavirus' in entry_str:
            info['virus_type'] = 'Rotavirus'
        elif 'Chicken anemia virus' in entry_str:
            info['virus_type'] = 'Chicken anemia virus'
        elif 'Rabies' in entry_str:
            info['virus_type'] = 'Rabies'
        elif 'Ebola' in entry_str:
            info['virus_type'] = 'Ebola'
        elif 'HIV' in entry_str:
            info['virus_type'] = 'HIV'
        elif 'Papillomavirus' in entry_str or 'papillomavirus' in entry_str:
            info['virus_type'] = 'Papillomavirus'
        elif 'respiratory syncytial' in entry_str.lower() or 'RSV' in entry_str:
            info['virus_type'] = 'RSV'
        elif 'Morbillivirus' in entry_str or 'distemper' in entry_str.lower():
            info['virus_type'] = 'Morbillivirus'
        elif 'parvovirus' in entry_str.lower():
            info['virus_type'] = 'Parvovirus'
        elif 'adenovirus' in entry_str.lower():
            info['virus_type'] = 'Adenovirus'
        elif 'Mumps' in entry_str or 'Orthorubulavirus' in entry_str:
            info['virus_type'] = 'Mumps'
        elif 'Measles' in entry_str:
            info['virus_type'] = 'Measles'
        elif 'Enterovirus' in entry_str or 'enterovirus' in entry_str:
            info['virus_type'] = 'Enterovirus'
        elif 'Herpes' in entry_str or 'herpes' in entry_str:
            info['virus_type'] = 'Herpesvirus'
        elif 'Polyomavirus' in entry_str or 'polyomavirus' in entry_str:
            info['virus_type'] = 'Polyomavirus'
        elif 'Astrovirus' in entry_str:
            info['virus_type'] = 'Astrovirus'
        elif 'Sapovirus' in entry_str:
            info['virus_type'] = 'Sapovirus'
        elif 'Calicivirus' in entry_str:
            info['virus_type'] = 'Calicivirus'
        elif 'Picornavirus' in entry_str or 'Rhinovirus' in entry_str:
            info['virus_type'] = 'Picornavirus'
        elif 'Metapneumovirus' in entry_str:
            info['virus_type'] = 'Metapneumovirus'
        elif 'Parainfluenza' in entry_str:
            info['virus_type'] = 'Parainfluenza'
        elif 'Bocavirus' in entry_str:
            info['virus_type'] = 'Bocavirus'
        elif 'PRRS' in entry_str or 'reproductive and respiratory syndrome' in entry_str.lower():
            info['virus_type'] = 'PRRS'
        elif 'Rotavirus' in entry_str or 'rotavirus' in entry_str:
            info['virus_type'] = 'Rotavirus'
        elif 'Circovirus' in entry_str or 'circovirus' in entry_str:
            info['virus_type'] = 'Circovirus'
        elif 'Coronavirus' in entry_str or 'coronavirus' in entry_str:
            info['virus_type'] = 'Coronavirus'
        elif 'Arenavirus' in entry_str:
            info['virus_type'] = 'Arenavirus'
        elif 'Hantavirus' in entry_str:
            info['virus_type'] = 'Hantavirus'
        elif 'Lyssavirus' in entry_str:
            info['virus_type'] = 'Lyssavirus'
        elif 'Flavivirus' in entry_str:
            info['virus_type'] = 'Flavivirus'
        elif 'Alphavirus' in entry_str:
            info['virus_type'] = 'Alphavirus'
        elif 'Bunyavirus' in entry_str or 'bunyavirus' in entry_str:
            info['virus_type'] = 'Bunyavirus'
        elif 'Deltacoronavirus' in entry_str:
            info['virus_type'] = 'Deltacoronavirus'
        elif 'Echovirus' in entry_str or 'echovirus' in entry_str:
            info['virus_type'] = 'Echovirus'
        elif 'Norwalk' in entry_str:
            info['virus_type'] = 'Norovirus'
        elif 'Foot-and-mouth' in entry_str or 'FMDV' in entry_str:
            info['virus_type'] = 'FMDV'
        elif 'Coxsackie' in entry_str or 'coxsackie' in entry_str:
            info['virus_type'] = 'Coxsackievirus'
        elif 'Poliovirus' in entry_str or 'polio' in entry_str.lower():
            info['virus_type'] = 'Poliovirus'
        elif 'Japanese encephalitis' in entry_str:
            info['virus_type'] = 'Japanese Encephalitis'
        elif 'Tick-borne' in entry_str or 'TBEV' in entry_str:
            info['virus_type'] = 'Tick-borne Encephalitis'
        elif 'Powassan' in entry_str:
            info['virus_type'] = 'Powassan'
        elif 'Marburg' in entry_str:
            info['virus_type'] = 'Marburg'
        elif 'Lassa' in entry_str:
            info['virus_type'] = 'Lassa'
        elif 'Crimean-Congo' in entry_str or 'CCHF' in entry_str:
            info['virus_type'] = 'CCHF'
        elif 'Rift Valley' in entry_str:
            info['virus_type'] = 'Rift Valley Fever'
        
        # Extract host
        host_patterns = ['chicken', 'human', 'swine', 'duck', 'turkey', 'dove', 'pigeon', 'avian', 'mallard', 'goose']
        for h in host_patterns:
            if h.lower() in entry_str.lower():
                info['host'] = h
                break
        
        # Extract year (4 digits)
        year_match = re.search(r'[/\-](\d{4})[/\)\-]', entry_str)
        if year_match:
            info['year'] = int(year_match.group(1))
        
        # Extract location
        # Known hosts/animals to filter out (expanded list)
        known_hosts = [
            'chicken', 'human', 'swine', 'duck', 'turkey', 'dove', 'pigeon',
            'avian', 'mallard', 'goose', 'cat', 'cattle', 'teal', 'environment',
            'wild bird', 'canine', 'feline', 'equine', 'seal', 'whale', 'mink',
            'blue-winged', 'northern pintail', 'cinnamon', 'crow', 'robin', 'pelican',
            'wigeon', 'widgeon', 'eagle', 'owl', 'swan', 'vulture', 'kittiwake',
            'jay', 'bufflehead', 'eider', 'goldeneye', 'grackle', 'merganser',
            'raven', 'tern', 'hawk', 'cougar', 'dolphin', 'grebe', 'starling',
            'flamingo', 'fox', 'gadwall', 'gull', 'scaup', 'shoveler', 'osprey',
            'peafowl', 'falcon', 'raccoon', 'crane', 'sanderling', 'skunk',
            'egret', 'sparrow', 'scoter', 'american', 'common', 'great', 'red',
            'black', 'white', 'northern', 'western', 'bald', 'barn', 'snowy',
            'trumpeter', 'mute', 'sand', 'sandhill', 'herring', 'glaucous',
            'rough-legged', 'sharp-shinned', 'red-shouldered', 'red-tailed',
            'red-breasted', 'white-winged', 'black-legged', 'great horned',
            'cooper', 'fish', 'european', 'eared', 'lesser', 'peregrine'
        ]

        # US State abbreviation to full name mapping (for map coordinates)
        us_state_names = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming'
        }

        # Influenza nomenclature: A/Host/Location/ID/Year(Subtype)
        # or sometimes: A/Location/ID/Year(Subtype)
        loc_match = re.search(r'\(A/([^/]+)/([^/]+)/([^/]+)/', entry_str)
        if loc_match:
            seg1 = loc_match.group(1)
            seg2 = loc_match.group(2)

            # Check if seg1 is a host
            is_seg1_host = any(h.lower() in seg1.lower() for h in known_hosts)
            is_seg2_host = any(h.lower() in seg2.lower() for h in known_hosts)

            if is_seg1_host and not is_seg2_host:
                candidate = seg2
            elif not is_seg1_host:
                candidate = seg1
            else:
                candidate = None

            if candidate:
                # Convert US state abbreviations to full state names
                if candidate.upper() in us_state_names:
                    info['location'] = us_state_names[candidate.upper()]
                elif len(candidate) == 2 and candidate.isupper():
                    # Unknown 2-letter code, default to USA
                    info['location'] = 'USA'
                else:
                    info['location'] = candidate

        # Fallback to hardcoded patterns (country and state names)
        if not info['location']:
            location_patterns = [
                # US States (full names)
                ('North Carolina', 'North Carolina'), ('South Carolina', 'South Carolina'),
                ('North Dakota', 'North Dakota'), ('South Dakota', 'South Dakota'),
                ('West Virginia', 'West Virginia'), ('New Hampshire', 'New Hampshire'),
                ('New Jersey', 'New Jersey'), ('New York', 'New York'), ('New Mexico', 'New Mexico'),
                ('Rhode Island', 'Rhode Island'), ('California', 'California'), ('Texas', 'Texas'),
                ('Florida', 'Florida'), ('Georgia', 'Georgia'), ('Ohio', 'Ohio'),
                ('Michigan', 'Michigan'), ('Illinois', 'Illinois'), ('Pennsylvania', 'Pennsylvania'),
                ('Virginia', 'Virginia'), ('Washington', 'Washington'), ('Arizona', 'Arizona'),
                ('Massachusetts', 'Massachusetts'), ('Tennessee', 'Tennessee'), ('Indiana', 'Indiana'),
                ('Missouri', 'Missouri'), ('Wisconsin', 'Wisconsin'), ('Minnesota', 'Minnesota'),
                ('Colorado', 'Colorado'), ('Maryland', 'Maryland'), ('Alabama', 'Alabama'),
                ('Kentucky', 'Kentucky'), ('Oregon', 'Oregon'), ('Oklahoma', 'Oklahoma'),
                ('Connecticut', 'Connecticut'), ('Iowa', 'Iowa'), ('Utah', 'Utah'),
                ('Nevada', 'Nevada'), ('Arkansas', 'Arkansas'), ('Kansas', 'Kansas'),
                ('Mississippi', 'Mississippi'), ('Nebraska', 'Nebraska'), ('Idaho', 'Idaho'),
                ('Hawaii', 'Hawaii'), ('Maine', 'Maine'), ('Montana', 'Montana'),
                ('Delaware', 'Delaware'), ('Vermont', 'Vermont'), ('Alaska', 'Alaska'),
                ('Wyoming', 'Wyoming'), ('Louisiana', 'Louisiana'),
                # Countries
                ('Saudi Arabia', 'Saudi Arabia'), ('Brazil', 'Brazil'), ('Egypt', 'Egypt'),
                ('China', 'China'), ('Korea', 'Korea'), ('Japan', 'Japan'), ('Vietnam', 'Vietnam'),
                ('Thailand', 'Thailand'), ('Indonesia', 'Indonesia'), ('Malaysia', 'Malaysia'),
                ('Hong Kong', 'Hong Kong'), ('Taiwan', 'Taiwan'), ('India', 'India'),
                ('Russia', 'Russia'), ('Germany', 'Germany'), ('France', 'France'),
                ('UK', 'UK'), ('Italy', 'Italy'), ('Spain', 'Spain'),
                ('Canada', 'Canada'), ('Mexico', 'Mexico'), ('Australia', 'Australia'),
                ('Singapore', 'Singapore'), ('Philippines', 'Philippines'), ('Argentina', 'Argentina'),
                ('Colombia', 'Colombia'), ('Peru', 'Peru'), ('Venezuela', 'Venezuela'),
                ('Chile', 'Chile'), ('Ecuador', 'Ecuador'), ('Bolivia', 'Bolivia'),
                ('Nigeria', 'Nigeria'), ('South Africa', 'South Africa'), ('Kenya', 'Kenya'),
                ('Ghana', 'Ghana'), ('Uganda', 'Uganda'), ('Tanzania', 'Tanzania'),
                ('Pakistan', 'Pakistan'), ('Bangladesh', 'Bangladesh'), ('Nepal', 'Nepal'),
                ('Sri Lanka', 'Sri Lanka'), ('Myanmar', 'Myanmar'), ('Cambodia', 'Cambodia'),
                ('Laos', 'Laos'), ('Puerto Rico', 'Puerto Rico'), ('Dominican', 'Dominican Republic'),
                ('Jamaica', 'Jamaica'), ('Haiti', 'Haiti'), ('Cuba', 'Cuba'),
                ('Guatemala', 'Guatemala'), ('Honduras', 'Honduras'), ('Nicaragua', 'Nicaragua'),
                ('Costa Rica', 'Costa Rica'), ('Panama', 'Panama'), ('Ireland', 'Ireland'),
                ('Netherlands', 'Netherlands'), ('Belgium', 'Belgium'), ('Poland', 'Poland'),
                ('Sweden', 'Sweden'), ('Norway', 'Norway'), ('Denmark', 'Denmark'),
                ('Finland', 'Finland'), ('Portugal', 'Portugal'), ('Greece', 'Greece'),
                ('Turkey', 'Turkey'), ('Israel', 'Israel'), ('Iran', 'Iran'),
                ('Iraq', 'Iraq'), ('Saudi', 'Saudi Arabia'), ('UAE', 'UAE'),
                ('Morocco', 'Morocco'), ('Algeria', 'Algeria'), ('Tunisia', 'Tunisia'),
                ('Ethiopia', 'Ethiopia'), ('Senegal', 'Senegal'), ('Cameroon', 'Cameroon'),
                ('Congo', 'Congo'), ('Angola', 'Angola'), ('Zimbabwe', 'Zimbabwe'),
                ('Zambia', 'Zambia'), ('Malawi', 'Malawi'), ('Mozambique', 'Mozambique')
            ]
            for pattern, location in location_patterns:
                if pattern in entry_str:
                    info['location'] = location
                    break

        # Additional patterns for isolate codes (e.g., CANDEN = Canada Dengue)
        if not info['location']:
            isolate_codes = {
                'CAN': 'Canada', 'USA': 'USA', 'BRA': 'Brazil', 'MEX': 'Mexico',
                'CHN': 'China', 'JPN': 'Japan', 'KOR': 'Korea', 'THA': 'Thailand',
                'VNM': 'Vietnam', 'IDN': 'Indonesia', 'MYS': 'Malaysia', 'SGP': 'Singapore',
                'PHL': 'Philippines', 'IND': 'India', 'PAK': 'Pakistan', 'BGD': 'Bangladesh',
                'AUS': 'Australia', 'NZL': 'New Zealand', 'GBR': 'UK', 'DEU': 'Germany',
                'FRA': 'France', 'ITA': 'Italy', 'ESP': 'Spain', 'NLD': 'Netherlands',
                'RUS': 'Russia', 'EGY': 'Egypt', 'ZAF': 'South Africa', 'NGA': 'Nigeria',
                'ARG': 'Argentina', 'COL': 'Colombia', 'PER': 'Peru', 'CHL': 'Chile',
                'PRI': 'Puerto Rico', 'DOM': 'Dominican Republic'
            }
            # Try to match isolate codes at word boundaries
            for code, country in isolate_codes.items():
                if re.search(rf'\b{code}[A-Z]*\d', entry_str):
                    info['location'] = country
                    break

        # Additional "from COUNTRY" pattern (e.g., "from USA")
        if not info['location']:
            from_match = re.search(r'from (USA|China|Brazil|Japan|Korea|India|Russia|Germany|France|UK|Canada|Mexico|Australia)', entry_str)
            if from_match:
                info['location'] = from_match.group(1)

        # 3-letter country code in isolate name (e.g., /CHN/, /BRA/, /USA/)
        if not info['location']:
            code_match = re.search(r'/([A-Z]{2,3})/', entry_str)
            if code_match:
                code = code_match.group(1)
                country_codes = {
                    'CHN': 'China', 'BRA': 'Brazil', 'USA': 'USA', 'JPN': 'Japan',
                    'KOR': 'Korea', 'IND': 'India', 'RUS': 'Russia', 'DEU': 'Germany',
                    'FRA': 'France', 'GBR': 'UK', 'CAN': 'Canada', 'MEX': 'Mexico',
                    'AUS': 'Australia', 'THA': 'Thailand', 'VNM': 'Vietnam',
                    'IDN': 'Indonesia', 'MYS': 'Malaysia', 'PHL': 'Philippines',
                    'SGP': 'Singapore', 'NLD': 'Netherlands', 'IRL': 'Ireland',
                    'ZAF': 'South Africa', 'EGY': 'Egypt', 'NGA': 'Nigeria',
                    'ARG': 'Argentina', 'COL': 'Colombia', 'PER': 'Peru'
                }
                if code in country_codes:
                    info['location'] = country_codes[code]
        
        # Extract gene segment
        gene_patterns = ['NS1', 'NS2', 'M1', 'M2', 'NEP', 'VP1', 'RdRp', 'HA', 'NA', 'NP', 'PA', 'PB1', 'PB2']
        for g in gene_patterns:
            if g in entry_str:
                info['gene'] = g
                break
        
        parsed.append(info)
    
    return parsed


@analysis_bp.route('/virus-identity', methods=['POST'])
def analyze_virus_identity():
    """Analyze virus identity based on metadata."""
    try:
        db = current_app.db_manager
        conn = db.conn
        cursor = conn.cursor()
        
        # Get all records with occurrence_count > 1 (identical sequences found multiple times)
        cursor.execute("""
            SELECT record_id, dna_sequence, source_metadata, occurrence_count
            FROM genetic_records
            WHERE occurrence_count > 1
            ORDER BY occurrence_count DESC
            LIMIT 100
        """)
        identical_groups = cursor.fetchall()
        
        # Get virus type distribution
        cursor.execute("SELECT source_metadata FROM genetic_records WHERE source_metadata IS NOT NULL AND source_metadata != '[]'")
        all_metadata = cursor.fetchall()
        
        virus_types = {}
        hosts = {}
        locations = {}
        years = {}
        
        for row in all_metadata:
            metadata_str = row[0] if isinstance(row[0], str) else str(row[0]) if row[0] else None
            parsed_list = parse_metadata(metadata_str)
            for p in parsed_list:
                if p['virus_type']:
                    vt = p['virus_type'] + (' ' + p['subtype'] if p['subtype'] else '')
                    virus_types[vt] = virus_types.get(vt, 0) + 1
                if p['host']:
                    hosts[p['host']] = hosts.get(p['host'], 0) + 1
                if p['location']:
                    locations[p['location']] = locations.get(p['location'], 0) + 1
                if p['year']:
                    years[p['year']] = years.get(p['year'], 0) + 1
        
        # Sort by count
        virus_types = dict(sorted(virus_types.items(), key=lambda x: x[1], reverse=True)[:10])
        hosts = dict(sorted(hosts.items(), key=lambda x: x[1], reverse=True)[:5])
        locations = dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10])
        years = dict(sorted(years.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM genetic_records")
        total_records = cursor.fetchone()[0]
        
        return jsonify({
            "status": "success",
            "total_records": total_records,
            "identical_groups": len(identical_groups),
            "distribution": {
                "virus_types": virus_types,
                "hosts": hosts,
                "locations": locations,
                "years": years
            },
            "top_identical": [{
                "record_id": r[0],
                "sequence_preview": r[1][:125] + "..." if len(r[1]) > 125 else r[1],
                "occurrence_count": r[3]
            } for r in identical_groups[:10]]
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@analysis_bp.route('/combined-insights', methods=['POST'])
def combined_insights():
    """Combine ML engine analysis with virus metadata for deeper insights.
    
    데이터 계약(Data Contract): 모든 메트릭은 반드시 신뢰성 메타데이터와 함께 반환.
    메타 없는 숫자는 Observation Plane에서 표시 금지.
    """
    try:
        import hashlib
        from datetime import datetime as dt
        
        db = current_app.db_manager
        ml_service = current_app.ml_service
        conn = db.conn
        cursor = conn.cursor()
        
        # ===== 데이터 스냅샷 해시 생성 =====
        cursor.execute("SELECT COUNT(*), MAX(rowid) FROM genetic_records")
        count_row = cursor.fetchone()
        record_count = count_row[0] if count_row else 0
        max_rowid = count_row[1] if count_row else 0
        snapshot_string = f"{record_count}:{max_rowid}:{dt.now().strftime('%Y%m%d%H')}"
        data_snapshot_hash = hashlib.md5(snapshot_string.encode()).hexdigest()[:12]
        
        # ===== ML Model Info with Full Metadata =====
        ml_info = {
            "accuracy": None,  # None = 메타데이터 없음 표시
            "f1_score": None,
            "model_loaded": ml_service.model is not None,
            # 메타데이터 계약
            "meta": {
                "model_version": None,
                "data_snapshot_hash": data_snapshot_hash,
                "is_heuristic": True,  # 기본값: heuristic 기반
                "is_simulation": False,
                "test_set_size": None,
                "base_class": None,
                "trained_at": None
            }
        }
        
        if ml_service.model:
            try:
                import joblib
                import os
                metrics_path = current_app.config.get('MODEL_DIR', 'ml_models') + '/training_metrics.joblib'
                model_path = current_app.config.get('MODEL_FILE', 'ml_models/model.joblib')
                
                if os.path.exists(metrics_path):
                    metrics = joblib.load(metrics_path)
                    ml_info['accuracy'] = round(metrics.get('accuracy', 0) * 100, 1)
                    ml_info['f1_score'] = round(metrics.get('f1_score', 0) * 100, 1)
                    
                    # 메타데이터 채우기
                    ml_info['meta']['test_set_size'] = metrics.get('test_size', 0)
                    ml_info['meta']['base_class'] = 'Type A, Type B'
                    ml_info['meta']['is_heuristic'] = metrics.get('is_heuristic', True)
                    ml_info['meta']['trained_at'] = metrics.get('trained_at', None)
                    
                # 모델 버전 (파일 수정 시간 기반)
                if os.path.exists(model_path):
                    mtime = os.path.getmtime(model_path)
                    ml_info['meta']['model_version'] = dt.fromtimestamp(mtime).strftime('%Y%m%d_%H%M')
            except Exception as e:
                ml_info['meta']['error'] = str(e)
        
        # Get sample sequences for ML classification breakdown by virus type
        # OPTIMIZED: Reduce sample size and batch predictions to prevent memory issues
        cursor.execute("""
            SELECT dna_sequence, source_metadata 
            FROM genetic_records 
            WHERE source_metadata IS NOT NULL AND source_metadata != '[]'
            LIMIT 100
        """)
        samples = cursor.fetchall()
        
        # Batch predict to avoid repeated model calls causing memory issues
        predictions = {}
        if ml_service.model:
            try:
                for row in samples:
                    seq = row[0]
                    # Cache predictions by sequence hash (first 50 chars as key)
                    seq_key = seq[:50] if len(seq) > 50 else seq
                    if seq_key not in predictions:
                        pred_result = ml_service.predict(seq)
                        predictions[seq_key] = pred_result.get('predicted_type', 'Unknown')
            except Exception as pred_err:
                # If prediction fails, skip ML classification
                predictions = {}
        
        # Classify samples and correlate with metadata
        type_classification = {}  # {virus_type: {Type A: count, Type B: count}}
        host_classification = {}  # {host: {Type A: count, Type B: count}}
        
        for row in samples:
            seq = row[0]
            metadata_str = row[1] if isinstance(row[1], str) else str(row[1]) if row[1] else None
            parsed_list = parse_metadata(metadata_str)
            
            # Get cached prediction
            seq_key = seq[:50] if len(seq) > 50 else seq
            predicted_class = predictions.get(seq_key, 'Unknown')
            
            for p in parsed_list:
                # Virus type correlation
                if p['virus_type']:
                    vt = p['virus_type'] + (' ' + p['subtype'] if p['subtype'] else '')
                    if vt not in type_classification:
                        type_classification[vt] = {'Type A': 0, 'Type B': 0}
                    if predicted_class in type_classification[vt]:
                        type_classification[vt][predicted_class] += 1
                
                # Host correlation
                if p['host']:
                    if p['host'] not in host_classification:
                        host_classification[p['host']] = {'Type A': 0, 'Type B': 0}
                    if predicted_class in host_classification[p['host']]:
                        host_classification[p['host']][predicted_class] += 1
        
        # Calculate risk scores for cross-species potential
        risk_scores = []
        for host, counts in host_classification.items():
            total = counts['Type A'] + counts['Type B']
            if total > 0:
                # Higher diversity = higher risk
                diversity = min(counts['Type A'], counts['Type B']) / max(counts['Type A'], counts['Type B']) if max(counts['Type A'], counts['Type B']) > 0 else 0
                risk_scores.append({
                    'host': host,
                    'sample_count': total,
                    'type_a_ratio': round(counts['Type A'] / total * 100, 1),
                    'type_b_ratio': round(counts['Type B'] / total * 100, 1),
                    'diversity_score': round(diversity * 100, 1)
                })
        risk_scores.sort(key=lambda x: x['diversity_score'], reverse=True)
        
        # Get temporal distribution
        cursor.execute("SELECT source_metadata FROM genetic_records WHERE source_metadata IS NOT NULL")
        all_meta = cursor.fetchall()
        years_data = {}
        for row in all_meta:
            metadata_str = row[0] if isinstance(row[0], str) else str(row[0]) if row[0] else None
            parsed = parse_metadata(metadata_str)
            for p in parsed:
                if p['year']:
                    if p['year'] not in years_data:
                        years_data[p['year']] = 0
                    years_data[p['year']] += 1
        years_data = dict(sorted(years_data.items()))
        
        # ===== 추가 통계 메타데이터 =====
        cursor.execute("SELECT COUNT(*) FROM genetic_records")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT record_id) FROM genetic_records")
        unique_records = cursor.fetchone()[0]
        
        virus_type_count = len(type_classification)
        location_count = len(set(loc for scores in risk_scores for loc in [scores.get('host', '')]))
        
        # 지역 데이터 추출 (locations)
        locations_set = set()
        for row in all_meta:
            metadata_str = row[0] if isinstance(row[0], str) else str(row[0]) if row[0] else None
            parsed = parse_metadata(metadata_str)
            for p in parsed:
                if p.get('location'):
                    locations_set.add(p['location'])
        
        return jsonify({
            "status": "success",
            "ml_info": ml_info,
            "virus_type_classification": type_classification,
            "host_classification": host_classification,
            "cross_species_risk": risk_scores[:5],
            "temporal_distribution": years_data,
            
            # ===== 6개 스탯 카드 데이터 + 메타데이터 계약 =====
            "stats": {
                "total_records": {
                    "value": total_records,
                    "meta": {
                        "dedup_applied": unique_records != total_records,
                        "unique_count": unique_records,
                        "snapshot_hash": data_snapshot_hash
                    }
                },
                "virus_types": {
                    "value": virus_type_count,
                    "meta": {
                        "taxonomy_source": "NCBI Influenza Database",
                        "classification_method": "regex_pattern_matching",
                        "confidence": "medium" if virus_type_count > 0 else "none"
                    }
                },
                "locations": {
                    "value": len(locations_set),
                    "meta": {
                        "geo_inference": "metadata_string_parsing",
                        "coord_source": "hardcoded_mapping",
                        "coverage": list(locations_set)[:10]  # 최대 10개 샘플
                    }
                }
            },
            
            # ===== Observation Plane 신뢰성 메타 =====
            "observation_meta": {
                "generated_at": dt.now().isoformat(),
                "data_snapshot_hash": data_snapshot_hash,
                "sample_size": len(samples),
                "ml_model_loaded": ml_service.model is not None,
                "trust_level": "verified" if ml_info['accuracy'] and ml_info['accuracy'] > 70 else "experimental",
                "warnings": []
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500


@analysis_bp.route('/simulation/sequences', methods=['GET'])
def get_simulation_sequences():
    """Get sequences for simulation visualization with location data."""
    try:
        db = current_app.db_manager
        conn = db.conn
        cursor = conn.cursor()
        
        # Get limit from query params (default: fetch all up to 3M)
        limit = request.args.get('limit', 3000000, type=int)
        
        cursor.execute("""
            SELECT record_id, dna_sequence, source_metadata, birth_time
            FROM genetic_records
            WHERE source_metadata IS NOT NULL AND source_metadata != '[]'
            ORDER BY birth_time ASC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        sequences = []
        for row in rows:
            record_id, seq, meta_str, birth_time = row
            parsed_list = parse_metadata(meta_str)
            
            # Extract location and virus type
            location = 'Unknown'
            virus_type = 'Unknown'
            for p in parsed_list:
                if p.get('location'):
                    location = p['location']
                if p.get('virus_type'):
                    virus_type = p['virus_type']
                    if p.get('subtype'):
                        virus_type += ' ' + p['subtype']
            
            sequences.append({
                'id': record_id,
                'sequence_preview': seq[:50] + '...' if len(seq) > 50 else seq,
                'location': location,
                'virus_type': virus_type,
                'birth_time': birth_time
            })
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM genetic_records WHERE source_metadata IS NOT NULL AND source_metadata != '[]'")
        total = cursor.fetchone()[0]
        
        return jsonify({
            "status": "success",
            "sequences": sequences,
            "total": total,
            "limit": limit
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
