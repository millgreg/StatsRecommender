import argparse
import sys
import os
import json
from feature_extractor import FeatureExtractor
from feedback_generator import FeedbackGenerator

def main():
    parser = argparse.ArgumentParser(description="AFSR: Automated Feedback on Statistical Reporting")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a text file containing the Methods section")
    group.add_argument("--text", help="Raw text of the Methods section")
    parser.add_argument("--llm", action="store_true", help="Enable LLM-enhanced feedback (requires OPENAI_API_KEY)")
    parser.add_argument("--output", help="Path to save the feedback (JSON)")

    args = parser.parse_args()

    content = ""
    title = "Local Audit"

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
            title = os.path.basename(args.file)
    else:
        content = args.text

    if not content.strip():
        print("Error: Input content is empty.")
        sys.exit(1)

    print(f"--- AFSR Audit Started: {title} ---")
    
    # 1. Extract Features
    extractor = FeatureExtractor()
    print("Extracting statistical features...")
    features = extractor.extract_features(content)

    # 2. Generate Feedback
    generator = FeedbackGenerator()
    # Force deterministic if --llm is not set, or if API key is missing
    if not args.llm:
        # Temporarily unset API key for this call to ensure deterministic output
        original_api_key = generator.api_key
        generator.api_key = None
        feedback = generator.generate_feedback(title, content, features)
        generator.api_key = original_api_key
    else:
        print("Generating LLM-enhanced feedback (this may take a moment)...")
        feedback = generator.generate_feedback(title, content, features)

    # 3. Display Results
    print("\n" + "="*50)
    print("AUDIT RESULTS")
    print("="*50)
    
    # Check if we have LLM feedback or just deterministic
    if "llm_enhanced_feedback" in feedback:
        f = feedback["llm_enhanced_feedback"]
        print(f"Overall Score: {f.get('overall_score', 'N/A')}/10")
        print(f"Rigor Rating:  {f.get('rigor_rating', 'N/A')}")
        print("\nCRITICAL GAPS:")
        for gap in f.get("critical_gaps", []):
            print(f" - {gap}")
        print("\nACTIONABLE RECOMMENDATIONS:")
        for rec in f.get("actionable_recommendations", []):
            print(f" - {rec.get('item')}: {rec.get('issue')}")
            print(f"   Fix: {rec.get('recommendation')}")
    else:
        f = feedback # if api_key was None, it returns the deterministic flat structure
        print(f"Overall Score: {f.get('overall_score', 'N/A')}/10")
        print(f"Rigor Rating:  {f.get('rigor_rating', 'N/A')}")
        print("\nCRITICAL GAPS (Deterministic):")
        for gap in f.get("critical_gaps", []):
            print(f" - {gap}")
        print("\nSTRENGTHS:")
        for strength in f.get("strengths", []):
            print(f" - {strength}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"title": title, "features": features, "feedback": feedback}, f, indent=2)
        print(f"\nFull report saved to: {args.output}")

    print("\n--- Audit Complete ---")

if __name__ == "__main__":
    main()
