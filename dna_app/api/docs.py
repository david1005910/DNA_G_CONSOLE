from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import glob

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/enhance', methods=['POST'])
def enhance_document():
    from google import genai
    
    data = request.json
    content = data.get('content', '')
    model_id = data.get('model', 'gemini-2.5-flash')
    
    # 1. Get API Key
    db = current_app.db_manager
    api_key = db.get_metadata('gemini_api_key')
    
    if not api_key:
        return jsonify({"status": "error", "message": "Gemini API Key is not configured. Please set it in Settings."}), 400
        
    # 2. Configure Gemini Client
    client = genai.Client(api_key=api_key)
    
    # 3. Model Mapping (Future/Draft -> Stable)
    # Mapping based on provided supported models
    model_map = {
        'gpt-4o': 'gpt-4o',
        'gpt-4o-mini': 'gpt-4o-mini',
        'gemini-3-pro-preview': 'gemini-3-pro-preview',
        'gemini-3-flash-preview': 'gemini-3-flash-preview',
        'gemini-2.5-pro': 'gemini-2.5-pro',
        'gemini-2.5-flash': 'gemini-2.5-flash',
        'gemini-2.0-flash': 'gemini-2.0-flash',
        'gemini-1.5-pro': 'gemini-1.5-pro',
        'gemini-1.5-flash': 'gemini-1.5-flash',
        'gemini-1.5-flash-8b': 'gemini-1.5-flash-8b',
        'claude-3-5-sonnet-20240620': 'claude-3-5-sonnet-20240620'
    }
    real_model = model_map.get(model_id, 'gemini-2.5-flash')
    
    try:
        prompt = f"""
        You are a professional technical writer. 
        Enhance the readability, structure, and clarity of the following markdown document.
        - Improve formatting, use bullet points/headers where appropriate.
        - Fix grammar and awkward phrasing.
        - Preserve all original meaning and technical details.
        - Output ONLY the enhanced markdown content.
        
        Document Content:
        {content}
        """
        
        response = client.models.generate_content(
            model=real_model,
            contents=prompt
        )
        enhanced_text = response.text
        
        return jsonify({"status": "success", "enhanced_content": enhanced_text, "used_model": real_model})
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Gemini API Error: {str(e)}"}), 500

@docs_bp.route('/list', methods=['GET'])
def list_documents():
    """모든 문서 목록 조회 (DB 저장 문서)"""
    db = current_app.db_manager
    documents = db.get_all_documents()
    # 프론트엔드와 일치하도록 doc_id를 id로 변환
    for doc in documents:
        doc['id'] = doc.pop('doc_id')
    return jsonify({"status": "success", "documents": documents})

@docs_bp.route('/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """특정 문서 내용 조회"""
    db = current_app.db_manager
    doc = db.get_document(doc_id)
    if doc:
        # 프론트엔드와 일치하도록 doc_id를 id로 변환
        doc['id'] = doc.pop('doc_id')
        # If it's a system doc, load content from file
        if doc.get('source_type') == 'system' and doc.get('source_path'):
            try:
                with open(doc['source_path'], 'r', encoding='utf-8') as f:
                    doc['content'] = f.read()
            except Exception as e:
                doc['content'] = f"Error loading file: {e}"
        return jsonify({"status": "success", "document": doc})
    return jsonify({"status": "error", "message": "Document not found"}), 404

@docs_bp.route('', methods=['POST'])
def create_document():
    """새 문서 생성"""
    data = request.json
    title = data.get('title', 'Untitled')
    content = data.get('content', '')
    
    doc_id = str(uuid.uuid4())
    db = current_app.db_manager
    
    success = db.create_document(doc_id, title, content, source_type='user')
    if success:
        return jsonify({"status": "success", "doc_id": doc_id, "message": "Document created"})
    return jsonify({"status": "error", "message": "Failed to create document"}), 500

@docs_bp.route('/<doc_id>', methods=['PUT'])
def update_document(doc_id):
    """문서 수정"""
    data = request.json
    title = data.get('title')
    content = data.get('content')
    enhanced_content = data.get('enhanced_content')
    
    db = current_app.db_manager
    success = db.update_document(doc_id, title=title, content=content, enhanced_content=enhanced_content)
    if success:
        return jsonify({"status": "success", "message": "Document updated"})
    return jsonify({"status": "error", "message": "Document not found or update failed"}), 404

@docs_bp.route('/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """문서 삭제"""
    db = current_app.db_manager
    success = db.delete_document(doc_id)
    if success:
        return jsonify({"status": "success", "message": "Document deleted"})
    return jsonify({"status": "error", "message": "Document not found"}), 404

@docs_bp.route('/sync-folder', methods=['POST'])
def sync_docs_folder():
    """docs 폴더의 md 파일들을 DB에 동기화"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs_dir = os.path.join(base_dir, 'docs')
    
    db = current_app.db_manager
    synced = []
    
    if os.path.exists(docs_dir):
        md_files = glob.glob(os.path.join(docs_dir, '*.md'))
        for md_path in md_files:
            filename = os.path.basename(md_path)
            title = filename.replace('.md', '')
            doc_id = f"system_{title}"
            
            # Check if already exists
            existing = db.get_document(doc_id)
            if not existing:
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    db.create_document(doc_id, title, content, source_type='system', source_path=md_path)
                    synced.append(title)
                except Exception as e:
                    print(f"Error syncing {filename}: {e}")
    
    return jsonify({"status": "success", "synced": synced, "count": len(synced)})

# Legacy endpoint for backward compatibility
@docs_bp.route('/save', methods=['POST'])
def save_document():
    data = request.json
    title = data.get('title', 'Untitled')
    content = data.get('content', '')
    
    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ' or c=='_']).rstrip()
    if not safe_title:
        safe_title = "Untitled"
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs_dir = os.path.join(base_dir, 'workspace', 'documents')
    
    os.makedirs(docs_dir, exist_ok=True)
    
    file_path = os.path.join(docs_dir, f"{safe_title}.md")
    
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return jsonify({"status": "success", "message": "Document saved", "path": file_path})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

