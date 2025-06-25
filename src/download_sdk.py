#!/usr/bin/env python3
"""
Simple downloader for OpenAI Agents SDK source code.
Downloads all Python files and saves them as markdown for easy reading.
"""

import os
import requests
import json
from pathlib import Path

def get_github_tree(owner, repo, path="", ref="main"):
    """Get file tree from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"
    response = requests.get(url)
    response.raise_for_status()
    
    tree = response.json()["tree"]
    # Filter for Python files in the specified path
    files = [
        item for item in tree 
        if item["type"] == "blob" and 
           item["path"].startswith(path) and 
           item["path"].endswith(".py")
    ]
    return files

def download_file(owner, repo, file_path, ref="main"):
    """Download raw file content from GitHub."""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{file_path}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def save_as_markdown(content, file_path, output_dir):
    """Save Python content as markdown with proper formatting."""
    # Create a descriptive filename
    # src/agents/core/agent.py -> agents_core_agent.md
    parts = file_path.split('/')
    if parts[0] == 'src':
        parts = parts[1:]  # Remove 'src'
    
    filename = '_'.join(parts).replace('.py', '.md')
    output_path = Path(output_dir) / filename
    
    # Create markdown content
    markdown_content = f"""# {file_path}

```python
{content}
```
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filename

def main():
    # Configuration
    owner = "openai"
    repo = "openai-agents-python"
    source_path = "src/agents"
    output_dir = Path(__file__).parent.parent / "data"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    print(f"Downloading OpenAI Agents SDK from {owner}/{repo}...")
    
    # Get all Python files
    files = get_github_tree(owner, repo, source_path)
    print(f"Found {len(files)} Python files")
    
    # Download and save each file
    saved_files = []
    for file_info in files:
        file_path = file_info["path"]
        print(f"Downloading {file_path}...")
        
        try:
            content = download_file(owner, repo, file_path)
            saved_name = save_as_markdown(content, file_path, output_dir)
            saved_files.append({
                "original_path": file_path,
                "saved_as": saved_name,
                "size": len(content)
            })
            print(f"  → Saved as {saved_name}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save index
    index_path = output_dir / "index.json"
    with open(index_path, 'w') as f:
        json.dump({
            "source": f"{owner}/{repo}",
            "path": source_path,
            "files": saved_files,
            "total_files": len(saved_files)
        }, f, indent=2)
    
    print(f"\nDownload complete! {len(saved_files)} files saved to {output_dir}")
    print(f"Index saved to {index_path}")

if __name__ == "__main__":
    main()