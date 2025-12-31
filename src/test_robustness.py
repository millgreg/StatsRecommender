import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from feature_extractor import FeatureExtractor
from rule_based_feedback import RuleBasedFeedbackEngine

def test_robustness():
    print("--- AFSR Robustness & Sensitivity Analysis ---")
    
    extractor = FeatureExtractor()
    engine = RuleBasedFeedbackEngine()
    
    # Define Test Cases: (Category, Original Text, [Variants])
    # Targeted Logic:
    # 1. Randomization (Should trigger 'randomization' feature)
    # 2. Blinding (Should trigger 'blinding' feature)
    # 3. Normality (Should trigger 'normality_checks' feature)
    # 4. Power Analysis (Should trigger 'sample_size' feature)
    
    test_cases = [
        {
            "category": "Randomization",
            "base": "Patients were randomized to treatment or control groups.",
            "variants": [
                "Patients were randomly assigned to treatment or control.",
                "Allocation was performed using a random number generator.",
                "We used random allocation for the participants."
            ],
            "expected_feature": "randomization"
        },
        {
            "category": "Blinding",
            "base": "The study was double-blinded.",
            "variants": [
                "Participants and assessors were masked to group assignment.",
                "Blinding was maintained throughout the trial.",
                "The experiment was conducted in a single-blind manner."
            ],
            "expected_feature": "blinding"
        },
        {
             "category": "Normality Checks",
             "base": "Normality was assessed using the Shapiro-Wilk test.",
             "variants": [
                 "Distribution was checked for normality.",
                 "We used the Kolmogorov-Smirnov test to verify normal distribution.",
                 "Gaussian distribution was confirmed via histogram inspection."
             ],
             "expected_feature": "normality_checks"
        },
        {
            "category": "Power Analysis",
            "base": "Sample size was determined by power calculation.",
            "variants": [
                "We conducted a power analysis to determine sample size.",
                "G*Power was used to estimate the required number of subjects.",
                "Statistical power was set at 0.80 for the calculation."
            ],
            "expected_feature": "sample_size"
        }
    ]
    
    passed = 0
    total = 0
    
    for case in test_cases:
        print(f"\nTesting Category: {case['category']}")
        
        # 1. Baseline
        base_feats = extractor.extract_features(case["base"])
        base_res = engine.generate_feedback(base_feats, title="Clinical Trial") # Simulate CT context
        base_score = base_res["overall_score"]
        base_detected = base_feats.get(case["expected_feature"], {}).get("present", False)
        
        print(f"  [Base] '{case['base'][:40]}...' -> Detected: {base_detected} | Score: {base_score}")
        
        if not base_detected:
            print(f"  [CRITICAL FAIL] Base phrase failed to trigger feature '{case['expected_feature']}'!")
        
        # 2. Variants
        for var in case["variants"]:
            total += 1
            var_feats = extractor.extract_features(var)
            var_res = engine.generate_feedback(var_feats, title="Clinical Trial")
            var_score = var_res["overall_score"]
            var_detected = var_feats.get(case["expected_feature"], {}).get("present", False)
            
            # Comparison
            status = "PASS"
            if not var_detected:
                status = "FAIL (Detection Missed)"
            elif var_score != base_score:
                status = "FAIL (Score Mismatch)"
            
            if status == "PASS":
                passed += 1
                
            print(f"  [{status}] '{var[:40]}...' -> Detected: {var_detected} | Score: {var_score}")

    acc = (passed / total) * 100 if total > 0 else 0
    print(f"\nOverall Robustness Accuracy: {acc:.1f}% ({passed}/{total})")

if __name__ == "__main__":
    test_robustness()
