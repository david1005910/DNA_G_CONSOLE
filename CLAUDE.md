# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DNA Governance & Neural Analysis Console (DG-NAC) - A DNA sequence classification and management system that uses RandomForest ML models to classify DNA sequences into "Type A" or "Type B" based on GC content and k-mer motifs. The system integrates with NCBI E-Utilities for real-time genetic data acquisition.

## Commands

### Running the Server
```bash
# Install dependencies (first time)
pip install -r requirements.txt

# Start server (auto-trains model if not present)
python run.py
# Server runs at http://localhost:5001

# Docker alternative
docker-compose up --build
```

### Model Training
```bash
# Manual initial training
python train_model.py

# Retrain via API (requires data in DB)
curl -X POST http://localhost:5001/api/ml/retrain
```

### Verification Scripts
```bash
python verify_logic.py      # Verify ML logic
python verify_storage.py    # Verify database operations
python verify_refactor.py   # Verify refactoring correctness
```

## Architecture

### Backend (Flask)

**Entry Point**: `run.py` - Creates Flask app, auto-trains model if missing, runs server with `threaded=False` and `use_reloader=False` to prevent segfaults from OpenMP/NumPy conflicts.

**App Factory**: `dna_app/__init__.py` - Uses Flask application factory pattern. Services (MLService, XAIService, RecordService, DatabaseManager) are initialized in app context and attached to `current_app`.

**API Blueprints** (`dna_app/api/`):
- `records.py` - CRUD for DNA records, NCBI sample fetching
- `ml.py` - Model retraining, inspection, HuggingFace upload
- `analysis.py` - XAI analysis endpoints
- `database.py` - Direct DB introspection
- `system.py` - System status monitoring
- `docs.py` - Documentation serving

**Services** (`dna_app/services/`):
- `ml_service.py` - Loads classifier + scaler separately, runs manual pipeline (extract → scale → predict)
- `feature_extractor.py` - `BiologicalFeatureExtractor`: sklearn transformer extracting GC content, entropy, and 3-mer frequencies (66 features total)
- `sequence_feature_extractor.py` - Extended 5-mer extractor for sequence-specific training
- `xai_service.py` - LIME-based explainability
- `record_service.py` - NCBI integration, record management
- `huggingface_service.py` - Model upload to HF Hub

### ML Pipeline

**Training** (`train_model.py`):
1. Generates synthetic DNA with configurable GC bias and motif injection
2. Uses K-Means clustering on biological features to infer latent labels
3. Trains RandomForest classifier with sklearn Pipeline
4. Saves components separately: `dna_classifier.joblib` (classifier), `scaler_rf.joblib`, `feature_names.joblib`, `training_metrics.joblib`

**Inference**: Components loaded separately in MLService, manual pipeline: `BiologicalFeatureExtractor.transform() → StandardScaler.transform() → RandomForestClassifier.predict()`

### Frontend
Static React app served from `public/` directory. Single-page admin interface with tabs for records, API testing, and system status.

### Database
SQLite at `database/genetics.db`. Main table: `genetic_records` with fields: record_id, dna_sequence, birth_time, death_time, record_type, source_metadata.

## Key Configuration

`config.py` defines paths:
- `DB_FILE`: `database/genetics.db`
- `MODEL_FILE`: `ml_models/dna_classifier.joblib`
- `MODEL_DIR`: `ml_models/`

Environment variables set in `run.py` to prevent segfaults:
- `OMP_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `JOBLIB_START_METHOD=loky`

## API Endpoints

- `POST /api/records` - Create record with ML prediction
- `GET /api/records` - List records (optional `?type=DNA|RNA`)
- `POST /api/records/fetch_samples` - Fetch from NCBI
- `POST /api/ml/retrain` - Retrain from DB data
- `GET /api/ml/inspect` - Model introspection (weights, features)
- `POST /api/ml/sequence-train` - Train sequence-specific model
- `POST /api/ml/upload-huggingface` - Upload to HF Hub
