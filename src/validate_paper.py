import os
import json
import random
import sys

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def start_validation(input_folder="data/feedback", output_file="data/blind_validation.json", n=10):
    print("--- AFSR Blind Validation Tool ---")
    
    # Load existing validaton data
    validation_data = load_json(output_file)
    original_expert_data = load_json("data/expert_audit.json")
    
    # Get all feedback files
    if not os.path.exists(input_folder):
        print(f"Error: Feedback folder '{input_folder}' not found.")
        return

    all_files = [f for f in os.listdir(input_folder) if f.endswith(".json")]
    
    # Filter out papers that are already validated (in either file)
    processed_pmcids = set(validation_data.keys()) | set(original_expert_data.keys())
    
    candidates = []
    for f in all_files:
        # Check against filename (which usually matches PMCID/ID)
        if f not in processed_pmcids:
            candidates.append(f)
            
    if not candidates:
        print("No new papers to validate!")
        return
        
    # sample random papers
    sample_size = min(len(candidates), n)
    selected_files = random.sample(candidates, sample_size)
    
    print(f"Selected {sample_size} papers for manual review.\n")
    
    for idx, filename in enumerate(selected_files):
        print(f"--- Paper {idx+1}/{sample_size}: {filename} ---")
        
        filepath = os.path.join(input_folder, filename)
        data = load_json(filepath)
        
        # Extract info
        title = data.get("title", "Unknown Title")
        feedback = data.get("feedback", {})
        
        # Handle cases where feedback might be wrapped differently (LLM vs Deterministic)
        # But based on feedback_generator structure:
        if "deterministic_baseline" in feedback:
            # If wrapped in common struct
            det_feedback = feedback["deterministic_baseline"]
        else:
            # If directly the rule engine output
            det_feedback = feedback
            
        print(f"TITLE: {title}")
        print(f"SCORE: {det_feedback.get('overall_score', 'N/A')}/10")
        print("\nSYSTEM GENERATED FINDINGS:")
        
        findings = []
        
        # GAPS
        gaps = det_feedback.get("critical_gaps", [])
        if not gaps and "gaps" in det_feedback: gaps = det_feedback["gaps"] # Fallback

        for g in gaps:
            findings.append({"type": "GAP", "message": g["message"], "evidence": g.get("evidence", "")})
            
        # STRENGTHS
        strengths = det_feedback.get("strengths", [])
        for s in strengths:
            findings.append({"type": "STR", "message": s["message"], "evidence": s.get("evidence", "")})
            
        if not findings:
            print("  (No major findings)")
        
        paper_results = {
            "title": title,
            "correct_findings": [],
            "false_positives": [],
            "missed_gaps": []
        }
        
        # Review loop
        for finding in findings:
            print(f"\nType: {finding['type']}")
            print(f"Finding: {finding['message']}")
            print(f"Evidence: {finding['evidence']}")
            
            while True:
                choice = input("Is this Correct? [y]es / [n]o (False Positive) / [s]kip: ").lower().strip()
                if choice in ['y', 'yes']:
                    paper_results["correct_findings"].append(finding)
                    break
                elif choice in ['n', 'no']:
                    paper_results["false_positives"].append(finding)
                    break
                elif choice in ['s', 'skip']:
                    break
        
        # Ask for missed gaps (simple boolean for now, or text entry)
        print("\nDid the system miss any OBVIOUS statistical flaws? (e.g. no power calc when needed)")
        missed = input("Describe key missed item (or press Enter if none): ").strip()
        if missed:
            paper_results["missed_gaps"].append(missed)
            
        # Save to session data
        validation_data[filename] = paper_results
        save_json(output_file, validation_data)
        print("Saved.\n")
        
    print(f"Validation Session Complete. Results saved to {output_file}")

if __name__ == "__main__":
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except:
            pass
    start_validation(n=count)
