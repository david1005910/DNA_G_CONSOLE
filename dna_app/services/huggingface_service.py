import os
import joblib
from huggingface_hub import HfApi
from config import config
import tempfile
from dna_app.services.model_card_template import get_model_card_content

class HuggingFaceService:
    def __init__(self):
        self.api = HfApi()

    def generate_model_card(self, metric_rf, metric_gb):
        """
        Generates the content for README.md (Model Card) using the template.
        """
        # Format metrics for the template
        acc_rf = f"{metric_rf.get('accuracy', 0)*100:.1f}%" if metric_rf else "N/A"
        f1_rf = f"{metric_rf.get('f1_score', 0)*100:.1f}%" if metric_rf else "N/A"
        
        acc_gb = f"{metric_gb.get('accuracy', 0)*100:.1f}%" if metric_gb else "N/A"
        f1_gb = f"{metric_gb.get('f1_score', 0)*100:.1f}%" if metric_gb else "N/A"
        dist_gb = metric_gb.get('label_distribution', {}) if metric_gb else {}

        return get_model_card_content(acc_rf, f1_rf, acc_gb, f1_gb, dist_gb)

    def upload_models(self, token: str, repo_id: str) -> dict:
        try:
            model_dir = config.MODEL_DIR if hasattr(config, 'MODEL_DIR') else 'ml_models'
            
            # 1. Load Metrics for Model Card
            path_rf = os.path.join(model_dir, "training_metrics.joblib")
            path_gb = os.path.join(model_dir, "sequence_metrics.joblib")
            
            metric_rf = joblib.load(path_rf) if os.path.exists(path_rf) else None
            metric_gb = joblib.load(path_gb) if os.path.exists(path_gb) else None
            
            # 2. Generate README.md
            readme_content = self.generate_model_card(metric_rf, metric_gb)
            readme_path = os.path.join(model_dir, "README.md")
            with open(readme_path, "w", encoding='utf-8') as f:
                f.write(readme_content)
            
            # 3. List files
            files_to_upload = [
                "dna_classifier.joblib",
                "scaler_rf.joblib",      # New
                "sequence_model.joblib",
                "scaler_gb.joblib",      # New
                "feature_names.joblib",
                "sequence_metrics.joblib",
                "training_metrics.joblib",
                "inference.py",          # New
                "README.md"
            ]
            
            uploaded_files = []
            
            # Ensure repo exists (create if not)
            try:
                self.api.create_repo(repo_id=repo_id, token=token, exist_ok=True)
            except Exception as e:
                print(f"[HF Service] Note on create_repo: {e}")

            # 4. Upload
            for filename in files_to_upload:
                file_path = os.path.join(model_dir, filename)
                if os.path.exists(file_path):
                    print(f"[HF Service] Uploading {filename}...")
                    self.api.upload_file(
                        path_or_fileobj=file_path,
                        path_in_repo=filename,
                        repo_id=repo_id,
                        token=token,
                        repo_type="model",
                        commit_message=f"Upload {filename} via DNA Console (Portable Version)"
                    )
                    uploaded_files.append(filename)

            
            # Cleanup README
            if os.path.exists(readme_path):
                os.remove(readme_path)

            return {
                "status": "success", 
                "message": f"Uploaded {len(uploaded_files)} files (including Model Card) to {repo_id}",
                "uploaded": uploaded_files
            }

        except Exception as e:
            print(f"[HF Service] Error: {str(e)}")
            return {"status": "error", "message": str(e)}
