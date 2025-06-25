#!/usr/bin/env python3
"""
Download and index all configured SDKs
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server_dynamic import DynamicMCPServer


async def main():
    """Download and index all SDKs"""
    print("SDK Downloader and Indexer")
    print("=" * 50)
    
    # Create server instance (which loads configuration)
    server = DynamicMCPServer()
    
    # List configured SDKs
    sdks = server.registry.list_sdks()
    print(f"\nFound {len(sdks)} configured SDKs:")
    for sdk_id in sdks:
        config = server.registry.get_sdk(sdk_id)
        print(f"  - {sdk_id}: {config.get('name', sdk_id)}")
    
    print(f"\nStarting download and indexing process...")
    print(f"Cache directory: {server.cache_dir}")
    print(f"Data directory: {server.data_dir}")
    print(f"Index directory: {server.index_dir}")
    
    # Initialize all SDKs
    await server.initialize_sdks()
    
    print("\n" + "=" * 50)
    print("Download and indexing complete!")
    
    # Show statistics
    print("\nStatistics:")
    for sdk_id in sdks:
        index = server.indexer.get_index(sdk_id)
        if index:
            print(f"\n{index['name']}:")
            print(f"  Files: {len(index.get('files', []))}")
            print(f"  Classes: {len(index.get('classes', {}))}")
            print(f"  Functions: {len(index.get('functions', {}))}")


if __name__ == "__main__":
    asyncio.run(main())