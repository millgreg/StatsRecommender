from Bio import Entrez
import os
import time

# Set your email for Entrez (NCBI requirement)
Entrez.email = "greg@example.com" 

def search_pmc_trials(journal, count=5):
    """
    Search PMC for Clinical Trials in a specific high-impact journal.
    """
    query = f'"{journal}"[Journal] AND "Clinical Trial"[Publication Type] AND open access[filter]'
    print(f"Searching PMC for: {query}")
    
    handle = Entrez.esearch(db="pmc", term=query, retmax=count)
    record = Entrez.read(handle)
    handle.close()
    
    return record["IdList"]

def fetch_pmc_fulltext(pmcid):
    """
    Fetch full-text XML for a given PMCID.
    """
    print(f"Fetching full text for PMCID: {pmcid}")
    handle = Entrez.efetch(db="pmc", id=pmcid, rettype="xml", retmode="text")
    xml_data = handle.read()
    handle.close()
    return xml_data

def save_raw_xml(pmcid, xml_data, folder="data/raw"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, f"{pmcid}.xml")
    with open(file_path, "wb") as f:
        f.write(xml_data)
    print(f"Saved: {file_path}")

if __name__ == "__main__":
    journals = ["Nature Medicine", "The Lancet", "NEJM", "BMJ", "JAMA"]
    trials_per_journal = 20
    
    for journal in journals:
        print(f"\n--- Processing Journal: {journal} ---")
        pmc_ids = search_pmc_trials(journal, count=trials_per_journal)
        print(f"Found IDs: {pmc_ids}")
        
        for pmcid in pmc_ids:
            try:
                # Check if file already exists to avoid redundant downloads
                if os.path.exists(os.path.join("data/raw", f"{pmcid}.xml")):
                    print(f"Skipping {pmcid}, already exists.")
                    continue
                    
                xml = fetch_pmc_fulltext(pmcid)
                save_raw_xml(pmcid, xml)
                # Be nice to NCBI servers
                time.sleep(1)
            except Exception as e:
                print(f"Error fetching {pmcid} for {journal}: {e}")
