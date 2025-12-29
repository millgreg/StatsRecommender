import os
import lxml.etree as ET
import json

def extract_methods_from_xml(xml_path):
    """
    Extract the Methods section from a PMC XML file.
    Identifies sections with 'methods' or 'statistics' in the title.
    """
    try:
        parser = ET.XMLParser(recover=True)
        tree = ET.parse(xml_path, parser=parser)
        root = tree.getroot()
        
        # PMC XML typically has sections in <body><sec>
        # We look for <sec> tags where the <title> matches our criteria
        sections = root.xpath(".//sec")
        
        extracted_data = {
            "title": "",
            "pmcid": os.path.basename(xml_path).replace(".xml", ""),
            "methods": [],
            "stats_reproducibility": []
        }
        
        # Extract Article Title
        article_title = root.xpath(".//article-title/text()")
        if article_title:
            extracted_data["title"] = "".join(article_title)

        for sec in sections:
            title_node = sec.find("title")
            if title_node is not None and title_node.text:
                title_text = title_node.text.lower()
                
                # Extract paragraph texts
                paragraphs = sec.xpath(".//p")
                content = "\n".join(["".join(p.itertext()) for p in paragraphs])
                
                if "methods" in title_text:
                    extracted_data["methods"].append({
                        "section_title": title_node.text,
                        "content": content
                    })
                
                if "statistics" in title_text or "reproducibility" in title_text:
                    extracted_data["stats_reproducibility"].append({
                        "section_title": title_node.text,
                        "content": content
                    })
                    
        return extracted_data
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
        return None

def process_raw_folder(raw_folder="data/raw", output_folder="data/processed"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for filename in os.listdir(raw_folder):
        if filename.endswith(".xml"):
            xml_path = os.path.join(raw_folder, filename)
            print(f"Processing: {filename}")
            data = extract_methods_from_xml(xml_path)
            
            if data:
                output_path = os.path.join(output_folder, filename.replace(".xml", ".json"))
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"Saved processed data to: {output_path}")

if __name__ == "__main__":
    process_raw_folder()
