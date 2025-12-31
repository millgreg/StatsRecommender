import os
import json
import pypdf
import re

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using pypdf.
    Attempts to identify the 'Methods' section heuristically.
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Simple heuristic to find Methods
        # Look for "Methods" or "Material and Methods" header
        # This is a basic fallback; for complex PDFs, layout analysis (pdfplumber) is better
        
        # Normalize simple headers
        lower_text = full_text.lower()
        
        # Try to find start of methods
        methods_start = -1
        for keyword in ["materials and methods", "methods", "study design"]:
            # Look for keyword on a line by itself or strong prominence
            # For raw text dump, we might just search for the substring
            idx = lower_text.find(keyword)
            if idx != -1:
                methods_start = idx
                break
        
        if methods_start != -1:
            # Try to find end of methods (Results, Discussion, etc.)
            end_candidates = ["results", "discussion", "conclusion", "references", "acknowledgements"]
            methods_end = len(full_text)
            
            # Search for the nearest end keyword after the proper methods start
            # (Note: lower_text indices match full_text indices approx 1:1)
            search_space = lower_text[methods_start:]
            
            closest_end = float('inf')
            for end_kw in end_candidates:
                e_idx = search_space.find(end_kw)
                if e_idx != -1 and e_idx < closest_end:
                    closest_end = e_idx
            
            if closest_end != float('inf'):
                methods_end = methods_start + closest_end
            
            methods_content = full_text[methods_start:methods_end]
            context = "Extracted Methods Section"
        else:
            # Fallback: Use full text if no clear Methods section found
            print(f"Warning: 'Methods' section not clearly identified in {os.path.basename(pdf_path)}. Using full text.")
            methods_content = full_text
            context = "Full Text (Methods not isolated)"

        return {
            "title": os.path.basename(pdf_path).replace(".pdf", ""),
            "pmcid": "PDF_" + os.path.basename(pdf_path).replace(" ", "_"),
            "methods": [{
                "section_title": context,
                "content": methods_content
            }],
            "stats_reproducibility": []
        }

    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None

def process_pdf_folder(input_folder="data/pdf_input", output_folder="data/processed"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"Created input folder: {input_folder}. Please put PDFs here.")
        return

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
    
    if not files:
        print(f"No PDF files found in {input_folder}.")
        return

    print(f"Found {len(files)} PDFs. Processing...")
    
    count = 0
    for filename in files:
        pdf_path = os.path.join(input_folder, filename)
        data = extract_text_from_pdf(pdf_path)
        
        if data:
            output_filename = filename.replace(".pdf", ".json").replace(".PDF", ".json")
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            print(f"Processed {filename} -> {output_filename}")
            count += 1
            
    print(f"Successfully processed {count} PDFs.")

if __name__ == "__main__":
    process_pdf_folder()
