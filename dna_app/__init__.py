from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from config import config
from .services.record_service import RecordService
from .services.ml_service import MLService
from .services.xai_service import XAIService
from .database.db_manager import DatabaseManager

def create_app():
    """애플리케이션 팩토리 함수."""
    # static_folder를 프로젝트 루트의 public으로 설정
    app = Flask(__name__, static_folder='../public')
    app.config.from_object(config)
    CORS(app)

    with app.app_context():
        db_manager = DatabaseManager(db_path=app.config['DB_FILE'])
        
        ml_service = MLService(model_path=app.config['MODEL_FILE'])
        xai_service = XAIService(model_dir=app.config['MODEL_DIR'])

        app.db_manager = db_manager  # docs.py에서 사용하기 위해 추가
        app.record_service = RecordService(db_manager=db_manager)
        app.ml_service = ml_service
        app.xai_service = xai_service
        print("[App Factory] Services initialized and attached to app context.")

    # 블루프린트 등록
    # 블루프린트 등록
    from .api import records, ml, system, database
    from .api.docs import docs_bp
    from .api.analysis import analysis_bp
    
    app.register_blueprint(records.bp, url_prefix='/api')
    app.register_blueprint(ml.bp, url_prefix='/api')
    app.register_blueprint(system.bp, url_prefix='/api')
    app.register_blueprint(database.bp, url_prefix='/api')
    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    print("[App Factory] API blueprints registered.")

    # 메인 페이지 라우트 (React App 서빙)
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # React 소스 코드 및 스타일 서빙
    @app.route('/src/<path:filename>')
    def serve_src(filename):
        return send_from_directory(os.path.join(app.static_folder, 'src'), filename)

    # Favicon route to suppress 404 error
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app
