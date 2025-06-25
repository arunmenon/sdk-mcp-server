#!/usr/bin/env python3
"""
Migration script to transition from OpenAI-specific to SDK-agnostic server
"""
import shutil
from pathlib import Path


def migrate():
    """Migrate from old structure to new"""
    print("Migrating to SDK-agnostic structure...")
    
    # Check if old data exists
    old_data = Path("data")
    if old_data.exists() and old_data.is_dir():
        # Check for old OpenAI SDK files
        old_files = list(old_data.glob("agents_*.md"))
        if old_files:
            print(f"Found {len(old_files)} OpenAI SDK files")
            
            # Create new structure
            new_dir = old_data / "openai_agents"
            new_dir.mkdir(exist_ok=True)
            
            # Move files
            for file in old_files:
                new_name = f"openai_agents_{file.name}"
                new_path = new_dir / new_name
                shutil.move(str(file), str(new_path))
                print(f"Moved {file.name} -> {new_path.name}")
    
    # Update any existing index files
    index_dir = Path("indices")
    if not index_dir.exists():
        index_dir.mkdir()
        print("Created indices directory")
    
    print("\nMigration complete!")
    print("\nNext steps:")
    print("1. Run: python src/download_sdks.py")
    print("2. Use: python src/server_dynamic.py")


if __name__ == "__main__":
    migrate()