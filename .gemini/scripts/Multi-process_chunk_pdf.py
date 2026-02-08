import xml.etree.ElementTree as ET
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

# Configuration
XML_FILE = 'docs/【书签】zephyr.xml'
SOURCE_PDF = 'docs/zephyr.pdf'
BASE_DIR = 'docs/chunk'

# Adjust concurrency based on CPU cores
MAX_WORKERS = 12 

def sanitize_name(name):
    """Sanitizes a string to be safe for directory names."""
    # Replace separators and illegal characters
    clean_name = re.sub(r'[\\/*?:"<>|]', '', name)
    # Replace colons with spaced dash for readability
    clean_name = clean_name.replace(':', ' -')
    # Collapse multiple spaces
    clean_name = " ".join(clean_name.split())
    return clean_name

def get_smart_structure(element, total_pages):
    """
    Parses XML to generate tasks based on Level 2 chunking strategy.
    
    Strategy:
    - Level 1 (Volume): Becomes a DIRECTORY.
    - Level 2 (Chapter): Becomes a FILE (includes all its sub-children).
    - Gap Handling: Content between L1 start and first L2 child becomes '00_Overview.pdf'.
    """
    tasks = []
    
    # Iterate Level 1 items (Volumes)
    l1_items = element.findall('ITEM')
    
    for i, l1 in enumerate(l1_items):
        l1_name = l1.get('NAME', f'Volume_{i}')
        l1_dir = sanitize_name(l1_name)
        
        try:
            l1_page = int(l1.get('PAGE', '0'))
            l1_page = max(0, l1_page - 1) # 0-based
        except ValueError:
            l1_page = 0
            
        # Determine L1 end page (start of next L1 or EOF)
        if i < len(l1_items) - 1:
            try:
                next_l1_page = int(l1_items[i+1].get('PAGE', str(total_pages)))
                next_l1_page = max(0, next_l1_page - 1)
            except:
                next_l1_page = total_pages
        else:
            next_l1_page = total_pages

        l1_output_path = os.path.join(BASE_DIR, l1_dir)
        
        # Get Level 2 items (Chapters)
        l2_items = l1.findall('ITEM')
        
        if not l2_items:
            # Case A: Level 1 has no children. It becomes a file itself.
            tasks.append({
                'name': l1_name,
                'start_page': l1_page,
                'end_page': next_l1_page,
                'path': BASE_DIR, # Saved in root of BASE_DIR
                'filename': f"{l1_dir}.pdf" 
            })
            continue

        # Case B: Level 1 has children. It becomes a directory.
        # Check for Overview (Gap between L1 start and first L2 start)
        try:
            first_l2_page = int(l2_items[0].get('PAGE', str(l1_page)))
            first_l2_page = max(0, first_l2_page - 1)
        except:
            first_l2_page = l1_page

        if first_l2_page > l1_page:
            tasks.append({
                'name': f"{l1_name} - Overview",
                'start_page': l1_page,
                'end_page': first_l2_page,
                'path': l1_output_path,
                'filename': "00_Overview.pdf"
            })

        # Process Level 2 items
        for j, l2 in enumerate(l2_items):
            l2_name = l2.get('NAME', f'Chapter_{j}')
            safe_l2_name = sanitize_name(l2_name)
            
            try:
                l2_page = int(l2.get('PAGE', '0'))
                l2_page = max(0, l2_page - 1)
            except:
                l2_page = 0
            
            # Determine End Page for L2
            # It ends at the start of the next L2, OR the end of L1 (if it's the last L2)
            if j < len(l2_items) - 1:
                try:
                    next_l2_page = int(l2_items[j+1].get('PAGE', str(next_l1_page)))
                    next_l2_page = max(0, next_l2_page - 1)
                except:
                    next_l2_page = next_l1_page
                
                # Special handling: nested bookmarks might have same page. 
                # Ensure we define a valid range, or defer to L1 limit.
                end_page = next_l2_page
            else:
                end_page = next_l1_page
            
            # Clamp end_page to next_l1_page to prevent leaking into next volume
            end_page = min(end_page, next_l1_page)
            
            # Create task for L2 (aggregated)
            tasks.append({
                'name': f"{l1_name} - {l2_name}",
                'start_page': l2_page,
                'end_page': end_page,
                'path': l1_output_path,
                'filename': f"{safe_l2_name}.pdf"
            })
            
    return tasks

def process_single_part(task):
    """
    Worker function to process a single split task.
    Executed in a separate process.
    """
    try:
        start_page = task['start_page']
        end_page = task['end_page']
        # Use explicit filename if provided, else default
        filename = task.get('filename', "source.pdf")
        output_filename = os.path.join(task['path'], filename)
        
        # Double check existence
        if os.path.exists(output_filename):
            return f"Skipped (Exists): {task['name']}"

        # Ensure directory exists
        os.makedirs(task['path'], exist_ok=True)

        # Skip empty ranges
        if start_page >= end_page:
             return f"Skipped (Empty): {task['name']} (pg {start_page}-{end_page})"

        # Performance Timer
        t0 = time.time()

        reader = PdfReader(SOURCE_PDF)
        total_pages = len(reader.pages)
        
        writer = PdfWriter()
        
        page_count = 0
        for p in range(start_page, min(end_page, total_pages)):
            writer.add_page(reader.pages[p])
            page_count += 1
        
        if page_count > 0:
            with open(output_filename, 'wb') as f:
                writer.write(f)
            duration = time.time() - t0
            return f"Completed: {task['name']} ({page_count} pgs) in {duration:.2f}s"
        else:
            return f"Skipped (No Content): {task['name']}"

    except Exception as e:
        return f"Error processing {task['name']}: {str(e)}"

def main():
    print(f"Parsing structure from {XML_FILE}...")
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        
        # In this XML schema, the root <BOOKMARKS> directly contains the Level 1 <ITEM>s.
        # So we pass 'root' directly to the structure builder.
        
        # 1. Get total pages first
        try:
            reader = PdfReader(SOURCE_PDF)
            total_pdf_pages = len(reader.pages)
            print(f"Source PDF loaded. Total pages: {total_pdf_pages}")
        except Exception as e:
            print(f"Error checking source PDF: {e}")
            return

        # 2. Build Smart Structure
        tasks = get_smart_structure(root, total_pdf_pages)
            
        print(f"Found {len(tasks)} distinct chunks (Level 2 aggregation).")
        
        if not tasks:
            print("No tasks generated.")
            return

        print(f"Starting execution with {MAX_WORKERS} PROCESSES...")
        
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_task = {executor.submit(process_single_part, task): task for task in tasks}
            
            with tqdm(total=len(tasks), unit="part") as pbar:
                for future in as_completed(future_to_task):
                    result = future.result()
                    if "Error" in result:
                        pbar.write(result)
                    # pbar.write(result) 
                    pbar.update(1)
                    
        print("\nAll tasks completed.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()