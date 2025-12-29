import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from feature_extractor import FeatureExtractor

def test_acronyms():
    extractor = FeatureExtractor()
    
    test_cases = [
        {
            "name": "False Positive: modification",
            "text": "The modification was successful.",
            "should_find_dic": False
        },
        {
            "name": "False Positive: medical",
            "text": "The medical study followed guidelines.",
            "should_find_dic": False
        },
        {
            "name": "True Positive: DIC uppercase",
            "text": "We evaluated the model using DIC.",
            "should_find_dic": True
        },
        {
            "name": "True Positive: Full term",
            "text": "The Deviance Information Criterion was used.",
            "should_find_dic": True
        }
    ]
    
    print("Running acronym extraction tests...")
    all_passed = True
    for case in test_cases:
        results = extractor.extract_features(case["text"])
        found = results["systematic_review_metrics"]["present"]
        passed = found == case["should_find_dic"]
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {case['name']} - Found: {found}")
        if not passed:
            all_passed = False
            
    if all_passed:
        print("\nAll tests passed! The strict acronym logic is working correctly.")
    else:
        print("\nSome tests failed. Please review the extraction rules.")

if __name__ == "__main__":
    test_acronyms()
