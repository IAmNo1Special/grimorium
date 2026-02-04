"""Magetools CLI - Command line interface for magetools.

Usage:
    python -m magetools init [directory]  - Generate manifest.json for a collection
    python -m magetools scan              - Scan and sync spells
    python -m magetools --help            - Show help
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def init_collection(directory: str) -> None:
    """Generate a manifest.json file for a collection directory.

    Args:
        directory: Path to the collection directory.
    """
    dir_path = Path(directory).resolve()

    if not dir_path.exists():
        print(f"❌ Directory does not exist: {dir_path}")
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"❌ Path is not a directory: {dir_path}")
        sys.exit(1)

    manifest_path = dir_path / "manifest.json"

    if manifest_path.exists():
        print(f"⚠️  manifest.json already exists at {manifest_path}")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            return

    # Count Python files to include in manifest
    py_files = list(dir_path.rglob("*.py"))
    public_py_files = [f for f in py_files if not f.name.startswith((".", "_"))]

    manifest = {
        "version": "1.0",
        "enabled": True,
        "description": f"Collection: {dir_path.name}",
        # No whitelist = all spells allowed
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Created manifest.json at {manifest_path}")
    print(f"   Found {len(public_py_files)} Python file(s) in collection.")
    print(f"   Collection '{dir_path.name}' is now enabled for strict mode.")


def scan_spells() -> None:
    """Scan and sync spells from .magetools directory."""
    from .spellsync import SpellSync, discover_and_load_spells

    print("🔍 Scanning for spells (strict_mode=True)...")

    registry: dict = {}
    discover_and_load_spells(registry=registry)

    if not registry:
        print("\n⚠️  No spells loaded!")
        print("Magetools runs in STRICT MODE by default.")
        print(
            "Ensure your tool folders contain a 'manifest.json' with '\"enabled\": true'."
        )
        print("\nTo enable a collection, run:")
        print("  python -m magetools init <path/to/collection>")
        return

    print(f"✅ Found {len(registry)} spell(s):")
    for name in sorted(registry.keys()):
        print(f"   • {name}")

    # Sync to vector store
    print("\n📦 Syncing to vector store...")
    try:
        spell_sync = SpellSync()
        spell_sync.sync_spells()
        print("✅ Sync complete!")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        print("   (This may be due to missing google-genai or chromadb)")


def main():
    """Main entry point for Magetools CLI."""
    parser = argparse.ArgumentParser(
        prog="magetools",
        description="Magetools - Dynamic tool discovery for AI agents",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Generate manifest.json for a collection directory",
    )
    init_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to collection directory (default: current directory)",
    )

    # scan command
    subparsers.add_parser(
        "scan",
        help="Scan and sync spells from .magetools directory",
    )

    args = parser.parse_args()

    if args.command == "init":
        init_collection(args.directory)
    elif args.command == "scan":
        scan_spells()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
