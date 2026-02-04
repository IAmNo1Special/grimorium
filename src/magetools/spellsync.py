import ast
import hashlib
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Any, List, Optional

import chromadb
from dotenv import load_dotenv

from .adapters import ChromaVectorStore, GoogleGenAIProvider
from .constants import (
    COLLECTION_ATTR_NAME,
    DB_FOLDER_NAME,
    MAGETOOLS_DIR_NAME,
    STANDARD_COLLECTION_NAME,
)
from .interfaces import EmbeddingProviderProtocol, VectorStoreProtocol

# from .spell_registry import spell_registry  <-- Removed global dependency

logger = logging.getLogger(__name__)


class SpellSync:
    """A magical synchronizer for matching and managing spells using Portable Spellbooks.

    Each subdirectory in the grimorium acts as a self-contained 'Grimorium' (Cartridge),
    containing its own ChromaDB database.
    """

    # Constants
    MAGETOOLS_ROOT = Path(MAGETOOLS_DIR_NAME)
    DB_FOLDER_NAME = DB_FOLDER_NAME
    STANDARD_COLLECTION_NAME = STANDARD_COLLECTION_NAME

    def __init__(
        self,
        root_path: Optional[Path] = None,
        allowed_collections: Optional[List[str]] = None,
        embedding_provider: Optional[EmbeddingProviderProtocol] = None,
        vector_store: Optional[VectorStoreProtocol] = None,
    ):
        """Initialize the SpellSync with a single unified database.

        Args:
            root_path: Optional path to the project root containing .grimorium.
                      If None, defaults to CWD.
            allowed_collections: Optional list of collection names to restrict access to.
                               If None, all collections are accessible.
        """
        load_dotenv()
        self.top_spells = 5
        # Distance threshold for filtering (Lower is better for distance metrics)
        # 0.0 = exact match, ~0.3-0.4 = Semantic match, >1.0 = Unrelated
        self.distance_threshold = 0.4
        self.distance_threshold = 0.4
        self.allowed_collections = allowed_collections
        self.registry = {}

        self.allowed_collections = allowed_collections
        self.registry = {}

        # Determine root path
        if root_path:
            self.MAGETOOLS_ROOT = root_path / MAGETOOLS_DIR_NAME
        else:
            self.MAGETOOLS_ROOT = Path(MAGETOOLS_DIR_NAME)

        # Unified Database Path: .magetools/.chroma_db
        db_path = self.MAGETOOLS_ROOT / self.DB_FOLDER_NAME

        # Ensure root grimorium folder exists
        if not self.MAGETOOLS_ROOT.exists():
            pass

        # Dependency Injection / Defaults
        if embedding_provider is None:
            self.embedding_provider = GoogleGenAIProvider()
        else:
            self.embedding_provider = embedding_provider

        if vector_store is None:
            self.vector_store = ChromaVectorStore(path=str(db_path))
        else:
            self.vector_store = vector_store

        self.embedding_function = self.embedding_provider.get_embedding_function()

    def __getstate__(self):
        """Custom pickling to exclude unpickleable objects."""
        state = self.__dict__.copy()
        if "client" in state:
            del state["client"]
        if "embedding_function" in state:
            del state["embedding_function"]
        return state

    def __setstate__(self, state):
        """Restore state and re-initialize unpickleable objects."""
        self.__dict__.update(state)
        # Re-initialize
        db_path = self.MAGETOOLS_ROOT / self.DB_FOLDER_NAME
        self.client = chromadb.PersistentClient(path=str(db_path))

    def get_grimorium_collection(self, collection_name: str):
        """Get or create a collection for a specific grimorium (folder)."""
        return self.vector_store.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
        )

    def find_matching_spells(self, query: str) -> list[str]:
        """Find spells that match the given query across all valid collections."""
        if not query or not isinstance(query, str) or not query.strip():
            logger.error("Error: Invalid query")
            return []

        logger.info(f"Searching for spells matching: {query[:50]}...")
        all_matches = []

        # List all collections in the DB
        # This is strictly faster than iterating the filesystem
        try:
            collections = self.vector_store.list_collections()
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

        for collection_obj in collections:
            coll_name = collection_obj.name

            # Filter by allowed_collections if set
            if self.allowed_collections is not None:
                if coll_name not in self.allowed_collections:
                    continue

            try:
                # We need to get the collection object with our embedding function attached
                # list_collections returns light objects without the EF
                collection = self.vector_store.get_collection(
                    name=coll_name, embedding_function=self.embedding_function
                )

                results = collection.query(
                    query_texts=[query],
                    n_results=self.top_spells,
                    include=["documents", "distances"],
                )

                if results and results["ids"] and results["ids"][0]:
                    ids = results["ids"][0]
                    dists = results["distances"][0]

                    for i, spell_id in enumerate(ids):
                        dist = dists[i]
                        all_matches.append((spell_id, dist))

            except Exception as e:
                logger.warning(f"Failed to search collection '{coll_name}': {e}")

        # Deduplicate matches keeping the lowest distance
        unique_matches_map = {}
        for spell_id, dist in all_matches:
            if (
                spell_id not in unique_matches_map
                or dist < unique_matches_map[spell_id]
            ):
                unique_matches_map[spell_id] = dist

        # Sort by distance
        sorted_matches = sorted(unique_matches_map.items(), key=lambda x: x[1])

        if sorted_matches:
            logger.debug(f"Matches before filtering (name, distance): {sorted_matches}")

        # Filter by threshold logic
        filtered_matches = [
            match for match in sorted_matches if match[1] <= self.distance_threshold
        ]

        # Return just the spell IDs (limited by top_spells)
        return [match[0] for match in filtered_matches][: self.top_spells]

    def validate_spell_access(self, spell_name: str) -> bool:
        """Check if a spell is allowed to be accessed by this instance."""
        # If no restrictions, everything is allowed
        if self.allowed_collections is None:
            return True

        # Use lists of collections to check (cache this?)
        # For now, query the DB to be sure it exists in an allowed collection
        try:
            for coll_name in self.allowed_collections:
                try:
                    collection = self.vector_store.get_collection(
                        name=coll_name, embedding_function=self.embedding_function
                    )
                    # Use get to check existence efficiently
                    res = collection.get(ids=[spell_name], include=[])
                    if res and res["ids"]:
                        return True
                except Exception:
                    continue

            logger.warning(
                f"Access denied: Spell '{spell_name}' not found in allowed collections: {self.allowed_collections}"
            )
            return False

        except Exception as e:
            logger.error(f"Error validating spell access: {e}")
            return False

    def sync_spells(self):
        """Synchronizes spells to the unified database, separated by collections."""
        logger.info("Starting unified spell synchronization...")

        all_spells = self.registry
        if not all_spells:
            return

        # Group spells by book (collection)
        book_buckets = {}
        for spell_name, spell_func in all_spells.items():
            # Determine collection from module name
            module_name = getattr(spell_func, "__module__", "")

            # Default to 'default' if unknown
            book_name = "default_grimorium"

            # Extract from module path: grimorium.discovered_spells.<book_name>.<file>
            if module_name and module_name.startswith("magetools.discovered_spells."):
                parts = module_name.split(".")
                if len(parts) >= 3:
                    book_name = parts[2]

            # Allow manual override
            if hasattr(spell_func, COLLECTION_ATTR_NAME):
                book_name = getattr(spell_func, COLLECTION_ATTR_NAME)

            if book_name not in book_buckets:
                book_buckets[book_name] = []
            book_buckets[book_name].append((spell_name, spell_func))

        # Process each bucket into its own collection
        for book_name, spells in book_buckets.items():
            logger.info(f"Syncing collection: {book_name}")

            try:
                collection = self.get_grimorium_collection(book_name)

                # Fetch existing metadata for diffing (same logic as before)
                existing_hashes = {}
                try:
                    result = collection.get(include=["metadatas"])
                    if result and result["ids"]:
                        for i, spell_id in enumerate(result["ids"]):
                            if result["metadatas"] and len(result["metadatas"]) > i:
                                meta = result["metadatas"][i]
                                if meta and "hash" in meta:
                                    existing_hashes[spell_id] = meta["hash"]
                except Exception:
                    existing_hashes = {}

                ids = []
                documents = []
                metadatas = []
                skipped = 0

                for spell_name, spell_func in spells:
                    docstring = spell_func.__doc__ or ""
                    current_hash = hashlib.md5(docstring.encode("utf-8")).hexdigest()

                    if (
                        spell_name in existing_hashes
                        and existing_hashes[spell_name] == current_hash
                    ):
                        skipped += 1
                        continue

                    ids.append(spell_name)
                    documents.append(docstring)
                    metadatas.append({"name": spell_name, "hash": current_hash})

                if ids:
                    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
                    logger.info(
                        f"Upserted {len(ids)} spells to collection '{book_name}'"
                    )

                if skipped > 0:
                    logger.info(f"Skipped {skipped} up-to-date spells in '{book_name}'")

            except Exception as e:
                logger.error(f"Failed to sync collection '{book_name}': {e}")

        logger.info("Unified spell synchronization complete.")


def discover_and_load_spells(
    root_path: Optional[Path] = None, registry: Optional[dict[str, Any]] = None
):
    """Dynamically discover and load spells from the .grimorium directory."""

    if root_path:
        search_path = root_path
    else:
        # Fallback to CWD-based default
        search_path = SpellSync.MAGETOOLS_ROOT.resolve()

    logger.info(f"Scanning for spells in strict mode: {search_path}")

    if not search_path.exists():
        logger.warning(
            f"Grimorium directory not found at {search_path}. "
            "Please create a '.grimorium' folder to store your spells."
        )
        return

    # Walk through all subdirectories in .grimorium
    # Each subdirectory is a collection
    for collection_dir in search_path.iterdir():
        if not collection_dir.is_dir() or collection_dir.name.startswith((".", "_")):
            continue

        collection_name = collection_dir.name
        logger.info(f"Found collection directory: {collection_name}")

        for py_file in collection_dir.rglob("*.py"):
            if py_file.name.startswith((".", "_")):
                continue

            # Module name includes collection to avoid collisions
            # e.g. grimorium.discovered_spells.arcane.fireball
            module_name = (
                f"magetools.discovered_spells.{collection_name}.{py_file.stem}"
            )

            try:
                # Pre-check syntax to avoid crashing on import
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()
                ast.parse(source)
            except Exception as e:
                logger.warning(f"Skipping {py_file} due to syntax/read error: {e}")
                continue

            try:
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # Tag the module with its collection for SpellSync to use
                    setattr(module, COLLECTION_ATTR_NAME, collection_name)

                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # SCAN FOR SPELLS
                    count = 0
                    for name, obj in inspect.getmembers(module):
                        if getattr(obj, "_grimorium_spell", False) is True:
                            # It's a spell!
                            # Register to the provided dict or just log it?
                            # We need to construct the registry key
                            # Key = {collection}.{func_name}
                            key = f"{collection_name}.{obj.__name__}"

                            if registry is not None:
                                registry[key] = obj
                                count += 1

                    if count > 0:
                        logger.info(
                            f"Loaded {count} spells from {py_file} into collection '{collection_name}'"
                        )
            except Exception as e:
                logger.warning(f"Warning: Failed to load spells from {py_file}: {e}")
