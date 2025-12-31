import json
import os
import random
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
from rule_based_feedback import RuleBasedFeedbackEngine

def generate_batch(n=20, output_file="validation_batch.txt"):
    print(f"Generating validation batch for {n} papers...")
    
    # Load all processed files
    processed_dir = "data/processed"
    all_files = [f for f in os.listdir(processed_dir) if f.endswith(".json")]
    
    # Exclude already audited (expert) and previously validated (blind)
    expert = json.load(open("data/expert_audit.json")) if os.path.exists("data/expert_audit.json") else {}
    blind = json.load(open("data/blind_validation.json")) if os.path.exists("data/blind_validation.json") else {}
    exclude = set(expert.keys()) | set(blind.keys())
    
    candidates = [f for f in all_files if f not in exclude]
    selected = random.sample(candidates, min(n, len(candidates)))
    
    engine = RuleBasedFeedbackEngine()
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"VALIDATION BATCH REPORT (N={len(selected)})\n")
        out.write("="*50 + "\n\n")
        
        for filename in selected:
            # Load processed data (text + features might be stale, but we need text to maybe re-extract? 
            # Actually, features are in data/feedback/*.json usually, but let's assume Processed file has what we need or we rely on existing features)
            # Wait, processed files contain 'methods' text. 
            # We need FEATURES. Phase 3 pipeline saved features to `data/feedback/`.
            # Let's verify if data/processed has features. 
            # The view_file output showed 'features' in data/feedback, but NOT in data/processed (it just bad 'methods').
            # So we load data/feedback/ for features.
            
            fb_path = os.path.join("data/feedback", filename)
            if not os.path.exists(fb_path):
                continue
                
            with open(fb_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            features = data.get("features", {})
            title = data.get("title", "")
            
            # Re-generate feedback with NEW rules (Observational logic)
            # RuleBasedFeedbackEngine.generate_feedback(features, title)
            res = engine.generate_feedback(features, title=title)
            
            # Write to report
            out.write(f"PAPER: {filename}\n")
            out.write(f"TITLE: {title}\n")
            
            # Classification
            is_obs = any("Observational" in s["message"] for s in res.get("strengths", []))
            out.write(f"TYPE: {'[OBSERVATIONAL]' if is_obs else '[CLINICAL/OTHER]'}\n")
            
            out.write("FINDINGS:\n")
            # Gaps
            for g in res.get("critical_gaps", []):
                out.write(f"  [GAP] {g['message']} | Ev: {g['evidence'][:100]}\n")
            
            # Strengths (only if relevant to misclassification checking)
            for s in res.get("strengths", []):
                 if "Observational" in s["message"]:
                     out.write(f"  [STR] {s['message']} | Ev: {s['evidence'][:100]}\n")
            
            out.write("-" * 50 + "\n")
            
    print(f"Batch report saved to {output_file}")

if __name__ == "__main__":
    generate_batch(20)
