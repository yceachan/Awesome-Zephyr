import os
import json

def generate_kb_index(root_dir="Knowledge_Base", output_file="Knowledge_Base/index.json"):
    """
    Scans the Knowledge_Base directory and generates a JSON index.
    Structure:
    {
        "Knowledge_Base": {
            "subdir": {
                "_files": ["file1.md", "file2.md"],
                "subsubdir": { ... }
            },
            "_files": ["root_file.md"]
        }
    }
    """
    index = {}

    # Normalize root_dir to avoid path separator issues
    root_dir = os.path.normpath(root_dir)
    parent_dir = os.path.dirname(root_dir)
    if not parent_dir:
        parent_dir = "."

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories (like .obsidian, .git)
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        
        # Relative path from the parent of Knowledge_Base (so "Knowledge_Base" is the top key)
        rel_path = os.path.relpath(dirpath, parent_dir)
        
        # Build the dictionary structure
        parts = rel_path.split(os.sep)
        current_level = index
        for part in parts:
            if part == ".": continue
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        # Filter for .md files
        md_files = [f for f in filenames if f.endswith('.md')]
        if md_files:
            # Sort for consistency
            md_files.sort()
            current_level['_files'] = md_files

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=4, ensure_ascii=False, sort_keys=True)
        print(f"Successfully generated index at {output_file}")
    except Exception as e:
        print(f"Error writing index file: {e}")

if __name__ == "__main__":
    # Determine absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir)) # Up 2 levels from .gemini/scripts
    
    kb_dir = os.path.join(project_root, "Knowledge_Base")
    output_json = os.path.join(kb_dir, "index.json")

    if os.path.exists(kb_dir):
        generate_kb_index(kb_dir, output_json)
    else:
        print(f"Error: Directory not found: {kb_dir}")
