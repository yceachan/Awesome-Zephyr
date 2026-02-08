import os
from pypdf import PdfReader

# Target files for the first batch of KB governance
TARGETS = [
    {
        "category": "Introduction",
        "file": "docs/chunk/Introduction/Distinguishing Features.pdf"
    },
    {
        "category": "Introduction",
        "file": "docs/chunk/Introduction/Fundamental Terms and Concepts.pdf"
    },
    {
        "category": "EnvSetup",
        "file": "docs/chunk/Developing with Zephyr/Getting Started Guide.pdf"
    }
]

def extract_text_from_pdf(path):
    if not os.path.exists(path):
        return f"[ERROR] File not found: {path}"
    
    try:
        reader = PdfReader(path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)
    except Exception as e:
        return f"[ERROR] reading {path}: {str(e)}"

def main():
    for item in TARGETS:
        print(f"=== PROCESSING: {item['file']} ===")
        content = extract_text_from_pdf(item['file'])
        # Print first 2000 chars to avoid token overflow, I will read full content internally if needed
        # but for this interaction, a summary/head is useful for the user to see I'm working.
        # Actually, I will print specific markers to separate them easily.
        print(f"--- START CONTENT: {item['category']} - {os.path.basename(item['file'])} ---")
        print(content[:3000]) # Extract enough for a summary
        print(f"--- END CONTENT ---\n")

if __name__ == "__main__":
    main()
