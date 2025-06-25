# Changelog

## [2.0.0] - SDK-Agnostic Framework

### Added
- **Multi-SDK Support**: Complete rewrite to support any AI/ML SDK
- **Dynamic Tool Generation**: Tools are created automatically based on SDK configuration
- **SDK Registry**: YAML-based configuration system (`sdks.yaml`)
- **Provider System**: Pluggable providers for different source types:
  - GitHub repositories
  - Direct URLs (ZIP/TAR archives)
- **Advanced Search**: Unified search engine with regex support
- **Cross-SDK Tools**: 
  - `list_available_sdks()` - Show all configured SDKs
  - `search_all_sdks()` - Search across multiple SDKs
  - `compare_implementations()` - Compare concepts across SDKs
- **Intelligent Indexing**: AST-based analysis of Python code
- **Concept Mapping**: Map similar concepts across different SDKs

### Changed
- Server architecture is now modular and extensible
- Download script now handles multiple SDKs
- File storage is organized by SDK
- Tools are prefixed with SDK identifier

### New Files
- `src/registry.py` - SDK configuration management
- `src/providers.py` - SDK download providers
- `src/indexer.py` - Code analysis and indexing
- `src/search.py` - Unified search engine
- `src/server_dynamic.py` - Dynamic MCP server
- `src/download_sdks.py` - Multi-SDK downloader
- `migrate_to_dynamic.py` - Migration helper

### Migration
Run `python migrate_to_dynamic.py` to migrate from v1.x structure.

## [1.0.0] - Initial Release

### Added
- Basic MCP server for OpenAI Agents SDK
- Simple file-based search
- Static tool definitions