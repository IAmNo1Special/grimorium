# Release Notes - Magetools v1.0.0 (MVP)

We are thrilled to announce the official **v1.0.0** release of **Magetools**! This release marks our transition from a technical preview to a production-ready MVP for AI agent tool discovery.

## 🚀 Key Features

### 🛡️ Strict Mode by Default
Security is our top priority. Magetools now operates in **Strict Mode**, requiring an explicit `manifest.json` for any collection of spells. This prevents unauthorized tool execution and allows developers to whitelist/blacklist specific functions.

### 🛠️ New CLI Suite
Managing your "Grimoriums" is now easier with built-in commands:
- `python -m magetools init`: Bootstrap a new collection with a security manifest.
- `python -m magetools scan`: Audit your tools and verify synchronization status.

### 🧩 Lean & Optional Dependencies
The core `magetools` package now only depends on `pyyaml`, keeping your distribution light. Advanced features like Google GenAI summaries or ChromaDB vector search are available via extras:
- `pip install magetools[google]`
- `pip install magetools[vectordb]`
- `pip install magetools[full]` (Includes everything)

### 🧪 Comprehensive Test Suite
Achieved 100% logic coverage across all core modules (`adapters`, `config`, `grimorium`, `spellsync`). The suite uses a mocked architecture, ensuring tests run instantly without external API dependencies.

## 🛠️ Internal Stability
- **Safer Initialization**: `Grimorium` now handles configuration errors gracefully, allowing agents to boot in a "degraded" state rather than crashing.
- **Async First**: Full support for `async await` lifecycle hooks for modern agentic frameworks.
- **Resource Management**: Implemented `BaseToolset.close()` to ensure database connections and AI clients are released properly.

## 📦 Getting Started
Verify your installation with the new scanner:
```bash
python -m magetools scan
```

---
**Full Documentation**: [README.md](./README.md)
**Changelog**: [CHANGELOG.md](./CHANGELOG.md)
