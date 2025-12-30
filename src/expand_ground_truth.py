from Bio import Entrez
import os
import time
import json
from pmc_fetcher import search_pmc_trials, fetch_pmc_fulltext, save_raw_xml
from xml_parser import process_raw_folder as process_raw_xml
from feature_extractor import process_processed_data as process_features_all
from feedback_generator import process_features as generate_feedback_all

Entrez.email = "greg@example.com"

def expand_dataset(target_total=100):
    # Get current IDs
    existing_ids = [f.replace(".xml", "") for f in os.listdir("data/raw") if f.endswith(".xml")]
    current_count = len(existing_ids)
    
    # We want to force add specific basic science papers, so we ignore the total count check
    # needed = target_total - current_count
    # if needed <= 0: ... return
    
    print(f"Current dataset size: {current_count}. Proceeding to expand with Basic Science papers...")

    # 1. Search for more papers
    # Target Basic Science Journals and Terms
    target_basic_science = 15
    needed = target_basic_science # Override to force fetching new ones regardless of total count
    
    print(f"Targeting {needed} new Basic Science papers...")

    journals = [
        "Nature Communications", 
        "Science Advances", 
        "PLOS Biology", 
        "eLife", 
        "Cell Reports"
    ]
    
    terms = [
        "Western Blot", 
        "CRISPR", 
        "Mice Model", 
        "In Vitro", 
        "Flow Cytometry",
        "Confocal Microscopy"
    ]
    
    queries = []
    for journal in journals:
        queries.append(f'"{journal}"[Journal] AND ("Western Blot" OR "CRISPR" OR "Mice") AND open access[filter] AND 2024[PDAT]')

    all_candidate_ids = []
    for query in queries:
        print(f"Searching: {query[:50]}...")
        try:
            handle = Entrez.esearch(db="pmc", term=query, retmax=10)
            record = Entrez.read(handle)
            handle.close()
            all_candidate_ids.extend(record["IdList"])
        except Exception as e:
            print(f"Search failed for {query}: {e}")
            time.sleep(2)
    
    # Remove duplicates and existing ones
    new_ids = [pid for pid in list(set(all_candidate_ids)) if pid not in existing_ids]
    
    print(f"Found {len(new_ids)} new candidate papers.")
    
    # 2. Fetch and Process
    fetch_count = 0
    for pid in new_ids:
        if fetch_count >= needed:
            break
        try:
            print(f"Fetching {pid} ({fetch_count+1}/{needed})...")
            xml = fetch_pmc_fulltext(pid)
            if xml:
                save_raw_xml(pid, xml)
                fetch_count += 1
                time.sleep(1) # NCBI throttle
        except Exception as e:
            print(f"Error fetching {pid}: {e}")

    if fetch_count > 0:
        # 3. Pipeline Run
        print("\n--- Running Parsing Pipeline ---")
        process_raw_xml() 
        
        print("\n--- Running Feature Extraction ---")
        process_features_all() 
        
        print("\n--- Generating Rule-Based Feedback ---")
        # Ensure we use the new RuleBasedFeedbackEngine
        from rule_based_feedback import process_all_features as process_feedback
        process_feedback()
    else:
        print("No new papers fetched.")

if __name__ == "__main__":
    expand_dataset(15) # Fetch 15 new basic science papers
