import os
import json
import traceback
from xml_parser import process_raw_folder
from feedback_generator import process_features as process_feedback
from feedback_generator import process_features as process_feedback
from feature_extractor import FeatureExtractor
from ingest_pdf import process_pdf_folder

def process_features_batch(processed_folder="data/processed", features_folder="data/features"):
    if not os.path.exists(features_folder):
        os.makedirs(features_folder)
        
    extractor = FeatureExtractor()
    count = 0
    
    processed_files = os.listdir(processed_folder)
    total = len([f for f in processed_files if f.endswith(".json")])
    
    for filename in processed_files:
        if filename.endswith(".json"):
            try:
                input_path = os.path.join(processed_folder, filename)
                
                with open(input_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                full_text = ""
                # Combine methods and stats sections
                for m in data.get("methods", []):
                    full_text += m.get("content", "") + "\n"
                for s in data.get("stats_reproducibility", []):
                    full_text += s.get("content", "") + "\n"
                
                if not full_text.strip():
                    print(f"Skipping {filename}: No text content extracted.")
                    continue
                    
                features = extractor.extract_features(full_text)
                
                output_data = {
                    "title": data.get("title"),
                    "pmcid": data.get("pmcid"),
                    "features": features
                }
                
                output_path = os.path.join(features_folder, filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2)
                
                count += 1
                if count % 10 == 0:
                    print(f"Extracted features for {count}/{total} papers...")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                # traceback.print_exc()

def run_pipeline():
    print("--- STEP 1: XML Parsing ---")
    process_raw_folder()
    
    print("\n--- STEP 1b: PDF Ingestion ---")
    process_pdf_folder()
    
    print("\n--- STEP 2: Feature Extraction ---")
    process_features_batch()
    
    print("\n--- STEP 3: Feedback Generation ---")
    process_feedback()
    
    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    run_pipeline()
