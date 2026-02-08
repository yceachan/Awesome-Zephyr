import xml.etree.ElementTree as ET
import os
from pypdf import PdfReader

# Configuration
XML_FILE = 'docs/【书签】zephyr.xml'
SOURCE_PDF = 'docs/zephyr.pdf'

def check_page_content(pdf_path, page_num):
    """Reads text from a specific page (0-based index) to verify content."""
    try:
        reader = PdfReader(pdf_path)
        if page_num < len(reader.pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            print(f"\n--- Content Check (Page {page_num + 1}, Index {page_num}) ---")
            print(text[:500] + "..." if len(text) > 500 else text) # Print first 500 chars
            print("---------------------------------------------------\n")
        else:
            print(f"Error: Page {page_num} is out of range.")
    except Exception as e:
        print(f"Error reading PDF: {e}")

def inspect_xml_structure(xml_path):
    """Parses XML and prints the hierarchy and logic."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Determine root container (WPS PDF XML usually wraps in <BOOKMARKS><ITEM>...</ITEM></BOOKMARKS>)
        main_book = root.find('ITEM')
        if not main_book:
            main_book = root
            
        print(f"XML Root: {root.tag}")
        
        l1_items = main_book.findall('ITEM')
        print(f"Found {len(l1_items)} Level 1 Items.")
        
        for i, l1 in enumerate(l1_items):
            name = l1.get('NAME', 'Unknown')
            page = l1.get('PAGE', 'Unknown')
            l2_items = l1.findall('ITEM')
            
            print(f"[L1] {name} (Page: {page}) -> Has {len(l2_items)} children")
            
            # Print first few children to verify logic
            for j, l2 in enumerate(l2_items[:3]): 
                l2_name = l2.get('NAME', 'Unknown')
                l2_page = l2.get('PAGE', 'Unknown')
                print(f"    - [L2] {l2_name} (Page: {l2_page})")
            
            if len(l2_items) > 3:
                print(f"    - ... and {len(l2_items) - 3} more")

    except Exception as e:
        print(f"Error parsing XML: {e}")

if __name__ == "__main__":
    print("=== Step 1: Verifying Page Content ===")
    # Check Page 15 (Index 14) as per XML 'Introduction'
    check_page_content(SOURCE_PDF, 14) 
    
    print("\n=== Step 2: Inspecting XML Logic ===")
    inspect_xml_structure(XML_FILE)
