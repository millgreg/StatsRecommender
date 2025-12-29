import json
import os

def verify_feedback(feedback_dir="data/feedback", expert_audit_path="data/expert_audit.json"):
    if not os.path.exists(expert_audit_path):
        print(f"Expert audit file not found at {expert_audit_path}")
        return

    with open(expert_audit_path, "r", encoding="utf-8") as f:
        expert_data = json.load(f)

    results = []
    
    for filename, expert_audit in expert_data.items():
        feedback_path = os.path.join(feedback_dir, filename)
        if not os.path.exists(feedback_path):
            print(f"Automated feedback for {filename} not found.")
            continue
            
        with open(feedback_path, "r", encoding="utf-8") as f:
            auto_data = json.load(f)
            
        # If it's mock feedback, skip verification or mark as mock
        if "mock_feedback" in auto_data.get("feedback", {}):
            print(f"Skipping {filename}: Only mock feedback available (API Key missing).")
            continue

        auto_feedback = auto_data.get("feedback", {})
        
        # Simple comparison of findings
        found_gaps = auto_feedback.get("critical_gaps", [])
        expert_gaps = expert_audit["expert_findings"]["gaps"]
        
        # Check if any expert gaps are captured in automated feedback
        captured = []
        missed = []
        for eg in expert_gaps:
            eg_lower = eg.lower()
            # Keywords to look for (heuristic)
            keywords = ["multiplicity", "blinding", "sample size", "normality", "itt", "interaction"]
            matched_keyword = next((k for k in keywords if k in eg_lower), None)
            
            if matched_keyword:
                match = any(matched_keyword in ag.lower() for ag in found_gaps)
            else:
                # Fallback to prefix match
                match = any(eg_lower[:20] in ag.lower() for ag in found_gaps)
                
            if match:
                captured.append(eg)
            else:
                missed.append(eg)
                
        results.append({
            "file": filename,
            "captured_gaps": captured,
            "missed_gaps": missed,
            "overall_match_rate": len(captured) / len(expert_gaps) if expert_gaps else 1.0
        })

    print(f"{'File':<25} | {'Captured':<10} | {'Missed':<10} | {'Match %':<10}")
    print("-" * 65)
    for r in results:
        print(f"{r['file']:<25} | {len(r['captured_gaps']):<10} | {len(r['missed_gaps']):<10} | {r['overall_match_rate']*100:>8.1f}%")

if __name__ == "__main__":
    verify_feedback()
