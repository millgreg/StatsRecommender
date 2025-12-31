import json
import os

def calculate_metrics(feedback_dir="data/feedback", expert_audit_path="data/expert_audit.json"):
    if not os.path.exists(expert_audit_path):
        print(f"Expert audit file not found at {expert_audit_path}")
        return

    with open(expert_audit_path, "r", encoding="utf-8") as f:
        expert_data = json.load(f)

    # Metric counters
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    keywords = [
        "multiplicity", "blinding", "sample size", "normality", "itt", 
        "interaction", "power", "imputation", "bayesian", "hierarchical", 
        "nri", "transitivity", "bootstrap", "inconsistency", "sucra", 
        "post hoc", "proportional hazards", "fragmentation", "recall", 
        "exclusion", "publication bias", "matching", "heterogeneity",
        "meta-analysis", "diagnostic", "roc", "auc", "nomogram",
        "sensitivity", "specificity", "complete case", "exact p-value",
        "multiple", "alpha", "threshold", "outcomes", "deviat",
        "categoriz", "i2", "nomogram", "auc", "roc", "crossover",
        "compliance", "attrition", "covariance", "effect size",
        "or", "hr", "rr", "md"
    ]

    synonyms = {
        "blinding": ["masking", "blinded", "masked"],
        "multiplicity": ["multiple comparisons", "bonferroni", "alpha adjustment", "hochberg", "multiple testing"],
        "imputation": ["missing data", "mice", "missing values", "random distribution"],
        "power": ["sample size justification", "power calculation", "calculated n"],
        "hierarchical": ["mixed-effect", "multilevel", "random effect", "mixed model"],
        "roc": ["auc", "diagnostic accuracy", "receiver operating"],
        "exclusion": ["attrition", "dropout", "crossover", "compliance", "deviat"],
        "heterogeneity": ["i2", "i-squared", "inconsistency"]
    }

    print(f"{'File':<25} | {'TP':<5} | {'FP':<5} | {'FN':<5} | {'Recall':<8} | {'Precision':<10}")
    print("-" * 75)

    for filename, expert_audit in expert_data.items():
        feedback_path = os.path.join(feedback_dir, filename)
        if not os.path.exists(feedback_path):
            continue
            
        with open(feedback_path, "r", encoding="utf-8") as f:
            auto_data = json.load(f)
            
        auto_feedback = auto_data.get("feedback", {})
        found_gaps = auto_feedback.get("critical_gaps", [])
        
        # Handle different expert audit formats
        if "expert_findings" in expert_audit:
            expert_gaps = expert_audit["expert_findings"].get("gaps", [])
        else:
            expert_gaps = expert_audit.get("critical_gaps", [])

        # 1. Identify TP and FN (Recall)
        tp = 0
        fn = 0
        captured_auto_indices = set()
        
        for eg in expert_gaps:
            eg_lower = eg.lower()
            
            # Find all relevant keywords and their synonyms for this expert gap
            relevant_terms = [k for k in keywords if k in eg_lower]
            for core, syn_list in synonyms.items():
                if core in eg_lower or any(s in eg_lower for s in syn_list):
                    relevant_terms.append(core)
                    relevant_terms.extend(syn_list)
            
            relevant_terms = list(set(relevant_terms)) # Deduplicate
            
            match_found = False
            for i, ag in enumerate(found_gaps):
                if i in captured_auto_indices: continue
                # Handle both string (legacy) and dict (new) formats
                if isinstance(ag, dict):
                    ag_str = ag.get("message", "")
                else:
                    ag_str = str(ag)
                    
                ag_lower = ag_str.lower()
                
                # Check for overlap between expert terms and automated gap
                if relevant_terms and any(t in ag_lower for t in relevant_terms):
                    match_found = True
                    captured_auto_indices.add(i)
                    break
                # Fallback to string overlap for short strings
                elif eg_lower[:20] in ag_lower:
                    match_found = True
                    captured_auto_indices.add(i)
                    break
            
            if match_found:
                tp += 1
            else:
                fn += 1

        # 2. Identify FP (Precision)
        # Any automated gap that didn't match an expert gap is considered a False Positive
        # (Assuming expert audit is exhaustive for our specific categories)
        fp = len(found_gaps) - len(captured_auto_indices)

        total_tp += tp
        total_fp += fp
        total_fn += fn

        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        
        print(f"{filename:<25} | {tp:<5} | {fp:<5} | {fn:<5} | {recall:>7.1%} | {precision:>9.1%}")

    # Global Metrics
    global_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    global_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    f1 = 2 * (global_precision * global_recall) / (global_precision + global_recall) if (global_precision + global_recall) > 0 else 0

    print("-" * 75)
    print(f"{'OVERALL':<25} | {total_tp:<5} | {total_fp:<5} | {total_fn:<5} | {global_recall:>7.1%} | {global_precision:>9.1%}")
    print(f"\nGlobal F1-Score: {f1:.3f}")

if __name__ == "__main__":
    calculate_metrics()
