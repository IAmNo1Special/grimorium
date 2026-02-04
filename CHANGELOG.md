# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-04

### Added
- **Dynamic Tool Discovery**: Core engine for identifying and loading Python functions as AI tools.
- **Strict Mode**: Security enforcement requiring `manifest.json` for all tool collections.
- **CLI Suite**: `uv run -m magetools init` and `uv run -m magetools scan` for collection management.
- **Provider Agnosticism**: Support for Google GenAI with automatic fallback to Mock providers.
- **Vector Search**: Integrated ChromaDB support for semantic tool lookups.
- **Modern Packaging**: Full migration to `uv` for dependency management and publishing.
- **Optional Dependencies**: Modular installation via extras (e.g., `magetools[google]`, `magetools[full]`).
- **Comprehensive Documentation**: Detailed MkDocs site with API references.
- **Resilient Initialization**: `auto_initialize` pattern with graceful error handling.

### Fixed
- Fixed blocking I/O in `Grimorium` constructor.
- Addressed security risks regarding arbitrary code execution via import sanitization and manifests.
- Optimized database locking issues during concurrent indexing.

### Security
- Introduced "Quarantine" mode for problematic spell files.
- Implemented permission-based tool execution.
