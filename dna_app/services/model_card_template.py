import os

def get_model_card_content(acc_rf, f1_rf, acc_gb, f1_gb, dist_gb):
    """
    Returns the content for the Hugging Face Model Card (README.md).
    Reads from HF_MODEL_CARD_TEMPLATE.md and fills in the metrics.
    """
    classes_list = ', '.join(dist_gb.keys()) if dist_gb else 'N/A'
    
    template_path = os.path.join(os.path.dirname(__file__), "HF_MODEL_CARD_TEMPLATE.md")
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Manually replace placeholders to avoid issues with code block curly braces
        content = content.replace("{acc_rf}", str(acc_rf))
        content = content.replace("{f1_rf}", str(f1_rf))
        content = content.replace("{acc_gb}", str(acc_gb))
        content = content.replace("{f1_gb}", str(f1_gb))
        content = content.replace("{classes_list}", str(classes_list))
        
        return content
        
    except FileNotFoundError:
        return f"Error: Template file not found at {template_path}"

