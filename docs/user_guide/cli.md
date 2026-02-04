# CLI Reference

Magetools provides a command-line interface for managing your tool collections.

## `python -m magetools init`

Initialize a new tool collection directory.

**Usage:**
```bash
python -m magetools init <directory>
```

**What it does:**
- Scans the directory for Python files.
- Creates a `manifest.json` file.
- Enables the collection for Strict Mode.

---

## `python -m magetools scan`

Audit your tools and verify synchronization status.

**Usage:**
```bash
python -m magetools scan
```

**What it does:**
- Discovers all tools in the `.magetools` directory.
- Verifies manifest validity.
- Indexes spells into the vector store.
- Reports any failed imports (Quarantine).
