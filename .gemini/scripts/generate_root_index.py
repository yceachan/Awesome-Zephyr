import os
import re
from datetime import datetime

ROOT_DIR = os.getcwd()
NOTEBOOK_DIR = os.path.join(ROOT_DIR, 'Knowledge_Base')
OUTPUT_FILE = os.path.join(ROOT_DIR, 'README.md')

IGNORE_DIRS = {'.gemini', '.obsidian', 'data', 'images', 'assets', 'raw'}
IGNORE_FILES = {'README.md'}  # Generally handle READMEs specifically as directory descriptions

def get_file_title(filepath):
    """Extracts the first H1 header from a markdown file, or uses filename."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception:
        pass
    
    # Fallback to filename without extension, replacing underscores with spaces
    filename = os.path.basename(filepath)
    name, _ = os.path.splitext(filename)
    return name.replace('_', ' ').replace('-', ' ').title()

def get_dir_description(dirpath):
    """Checks for a README.md in the directory to extract a description."""
    readme_path = os.path.join(dirpath, 'README.md')
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                # Expecting format: # Title \n\n Description...
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    # Return the first non-header, non-empty line as description
                    if line and not line.startswith('#'):
                        return line
        except:
            pass
    return None

def generate_tree_markdown(current_dir, level=2):
    """Recursively generates markdown list for the directory structure."""
    md_output = []
    
    # Get all items
    try:
        items = os.listdir(current_dir)
    except FileNotFoundError:
        return []

    # Separate directories and files
    dirs = []
    files = []
    
    for item in items:
        if item.startswith('.'): continue
        
        full_path = os.path.join(current_dir, item)
        
        if os.path.isdir(full_path):
            if item not in IGNORE_DIRS:
                dirs.append(item)
        elif item.endswith('.md'):
            if item not in IGNORE_FILES:
                files.append(item)
    
    # Sort for consistent output
    dirs.sort()
    files.sort()
    
    # Process files in current directory
    for file in files:
        full_path = os.path.join(current_dir, file)
        rel_path = os.path.relpath(full_path, ROOT_DIR).replace('\\', '/')
        title = get_file_title(full_path)
        indent = "  " * (level - 2)
        md_output.append(f"{indent}- [{title}]({rel_path})")

    # Process subdirectories
    for d in dirs:
        full_path = os.path.join(current_dir, d)
        
        # Directory Title: Try to make it pretty
        dir_title = d.replace('_', ' ').replace('-', ' ').title()
        
        # Check for README description
        desc = get_dir_description(full_path)
        desc_str = f": *{desc}*" if desc else ""
        
        indent = "  " * (level - 2)
        
        # Check if directory has content before printing header
        sub_content = generate_tree_markdown(full_path, level + 1)
        if sub_content:
            md_output.append(f"{indent}- **{dir_title}/** {desc_str}")
            md_output.extend(sub_content)
            
    return md_output

def main():
    print(f"Scanning {NOTEBOOK_DIR}...")
    
    # 1. Header Content
    header = f"""# Embedded Aimed Bluetooth Protocol Stack Knowledge Base

> **Auto-Generated Index**
> *Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

Based on `Bluetooth Core Specification v6.2` and `HOGP v1.1`.
This knowledge base is governed by the Gemini Agent and utilizes the `pdf` skill for accurate specification extraction.

---

## 📚 Knowledge Index

"""

    # 2. Generate Tree
    content_lines = generate_tree_markdown(NOTEBOOK_DIR)
    
    # 3. Footer / Tools
    footer = f"""
---

## 🚀 自动化工作流 (Automation Workflow)

本项目集成了自动化运维脚本，建议通过 `do.bat` 进行所有日常操作：

- **`do.bat`**: 核心自动化入口。依次运行 README 索引更新、JSON 索引生成，并引导完成 Git 提交流程。
  - 用法：`do -m "commit message"` (自动更新并提交)
  - 用法：`do --check` (仅更新并预览索引，不提交)

## 🛠️ 运维工具库 (Operational Tools)

这些脚本位于 `.gemini/scripts/`，用于维持知识库的结构化与准确性：

- **索引治理**:
  - `generate_root_index.py`: (本脚本) 自动扫描 `Knowledge_Base` 并重建根目录 `README.md` 导航树。
  - `generate_kb_index.py`: 为 Agent 生成结构化的 `index.json`，提升机器检索效率。
---

## 📜 License & Copyright

Copyright (c) {datetime.now().year} **yceachan** (<yceachan@foxmail.com>)

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
"""
    
    
    
    full_content = header + "\n".join(content_lines) + footer
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_content)
        
    print(f"Successfully generated README.md in {ROOT_DIR}")

if __name__ == "__main__":
    main()
