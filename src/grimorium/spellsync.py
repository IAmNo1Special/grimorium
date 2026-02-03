"""SpellSync - A magical system for managing and discovering spells.

This module provides functionality to register, discover, and manage magical spells
using semantic similarity and function decoration.
"""

import json
import logging
import re
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai.types import EmbedContentConfig
from sklearn.metrics.pairwise import cosine_similarity

from .models import SpellMetadata
from .spell_registry import spell_registry

logger = logging.getLogger(__name__)


class SpellSync:
    """A magical synchronizer for matching and managing spells based on semantic similarity.

    This class provides functionality to register, discover, and manage magical spells
    using function decoration and semantic search.

    Attributes:
        embedding_model (str): The name of the magical embedding model to use
        top_spells (int): Number of top spells to return in search results
        spells_data (List[Dict]): Loaded spell data with embeddings and metadata
        _spell_registry (Dict[str, SpellMetadata]): In-memory registry of all registered spells
    """

    # Hardcoded constants
    SPELL_REQUEST_PATTERN = r"<spell_request>\s*spell:\s*(.*?)\s*</spell_request>"
    DISPLAY_INDENT = 2
    DISPLAY_MAX_WIDTH = 120

    def __init__(self):
        """Initialize the SpellSync with configuration."""

        # Initialize instance variables
        self.embedding_model = "gemini-embedding-001"
        self.spell_request_pattern = re.compile(self.SPELL_REQUEST_PATTERN)
        self.top_spells = 5
        self.spells_data: List[Dict[str, Any]] = []

        # Initialize other components
        load_dotenv()
        self.client = genai.Client()

        # Load spells from tools_embeddings.json
        self._load_spells_data()

    def _load_spells_data(self) -> None:
        """Load spell data from tools_embeddings.json."""
        try:
            # Look for tools_embeddings.json in the same directory as this file
            tools_path = Path(__file__).parent / "tools_embeddings.json"

            if not tools_path.exists():
                logger.warning(f"Warning: {tools_path} not found. No spells loaded.")
                self.spells_data = []
                return

            logger.info(f"Loading spells from {tools_path}...")
            with open(tools_path, "r", encoding="utf-8") as f:
                tools_data = json.load(f)

            # Convert tools data to spells data format
            self.spells_data = []
            for tool in tools_data:
                try:
                    spell_metadata = SpellMetadata(
                        name=tool["name"],
                        docstring=tool["docstring"],
                        docstring_embedding=tool["docstring_embedding"],
                        created_at=tool["created_at"],
                    )
                    self.spells_data.append(spell_metadata)
                except KeyError as e:
                    logger.warning(f"Warning: Missing required field in tool data: {e}")
                    continue

            logger.info(
                f"Successfully loaded {len(self.spells_data)} spells from {tools_path}"
            )

        except json.JSONDecodeError as e:
            logger.error(f"Error: Invalid JSON in {tools_path}: {e}")
            self.spells_data = []
        except OSError as e:
            logger.error(f"Error reading {tools_path}: {e}")
            self.spells_data = []
        except Exception as e:
            logger.error(f"Unexpected error loading spells: {e}")
            self.spells_data = []

    def extract_spell_request(self, text: str) -> Optional[str]:
        """Extract spell descriptions from spell_request tags in text.

        Parses input text to find <spell_request> tags and extracts spell
        descriptions. The expected format is:
        <spell_request>spell: [spell description]</spell_request>

        Args:
            text (str): Input text potentially containing spell_request tags

        Returns:
            Optional[str]: The extracted spell description if found,
                or None if no matching tag is found.
        """
        match = self.spell_request_pattern.search(text)
        if match:
            spell_desc = match.group(1).strip()
            return spell_desc
        return None

    def _get_embedding(self, text: str, max_retries: int = 3) -> Optional[List[float]]:
        """Generate an embedding for the given text using the google genai model
        configured for semantic similarity.

        Args:
            text (str): The text to generate an embedding for.
            max_retries (int, optional): Maximum number of retry attempts on failure.
                Defaults to 3.

        Returns:
            List[float]: The embedding vector.
        """
        for attempt in range(max_retries):
            try:
                time.sleep(0.05)  # Avoid frequent requests
                response = self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                    config=EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
                )
                return response.embeddings[0].values
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # Exponential backoff strategy
                    logger.error(
                        f"Error getting embedding, retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to get embedding after {max_retries} attempts: {e}"
                    )
                    return None

    def _calculate_arcane_similarity(
        self, essence1: List[float], essence2: List[float]
    ) -> float:
        """
        Calculate the arcane resonance between two magical essences.

        This ancient formula measures how closely two magical patterns align in the aether.

        Args:
            essence1: The first magical essence vector
            essence2: The second magical essence vector

        Returns:
            float: The arcane resonance ratio, ranging from [-1, 1],
                  where 1 indicates perfect harmonic alignment and
                  -1 indicates complete opposition.
        """
        if not essence1 or not essence2:
            return 0.0

        essence1 = np.array(essence1).reshape(1, -1)
        essence2 = np.array(essence2).reshape(1, -1)

        # Check for void essence (zero vectors)
        norm1 = np.linalg.norm(essence1)
        norm2 = np.linalg.norm(essence2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return cosine_similarity(essence1, essence2)[0][0]

    def find_matching_spells(self, query: str) -> List[Dict[str, Any]]:
        """Find spells that match the given query using semantic similarity.

        Args:
            query: The search query to match against spells.

        Returns:
            A list of matching spells, sorted by relevance. Each spell is a dictionary
            containing at least 'name', 'description', and 'similarity_score'.

        Example:
            >>> spell_sync = SpellSync()
            >>> matches = spell_sync.find_matching_spells("get user information")
            >>> [m['name'] for m in matches]
            ['get_user_name', 'get_user_profile', ...]
        """
        if not query or not isinstance(query, str) or not query.strip():
            logger.error("Error: Invalid query")
            return []

        logger.info(f"Searching for spells matching: {query[:50]}...")

        # Get embedding for the query
        query_embedding = self._get_embedding(query)
        if query_embedding is None or not isinstance(
            query_embedding, (list, np.ndarray)
        ):
            logger.error("Error: Failed to get valid query embedding")
            return []

        # Calculate cosine similarity with all spells
        similarities = []
        for spell in self.spells_data:
            logger.debug(f"Processing spell: {spell.name}")
            try:
                if not spell or not isinstance(spell, SpellMetadata):
                    logger.warning("Warning: Invalid spell format")
                    continue

                spell_embedding = spell.docstring_embedding
                if not spell_embedding or not isinstance(
                    spell_embedding, (list, np.ndarray)
                ):
                    logger.warning(f"Warning: Invalid embedding for spell {spell.name}")
                    continue

                similarity = self._calculate_arcane_similarity(
                    query_embedding, spell_embedding
                )
                logger.debug(f"Similarity score for spell {spell.name}: {similarity}")
            except Exception as e:
                logger.error(f"Error processing spell {spell.name}: {str(e)}")
                continue
            similarities.append((spell.name, similarity))

        # Sort by similarity score (descending)
        try:
            similarities.sort(key=lambda x: x[1], reverse=True)
            logger.info(f"Found {len(similarities)} potential matches")
            return [spell_name for spell_name, _ in similarities[: self.top_spells]]
        except Exception as e:
            logger.error(f"Error sorting results: {e}")
            return []

    def match(self, input_text: str) -> Dict[str, Any]:
        """Match the input text to the most relevant spell using semantic similarity.

        This is the main method to find spells that match a natural language query.
        It first checks for exact name matches, then falls back to semantic search.

        Args:
            input_text: The input text to match against spells.

        Returns:
            A dictionary containing:
            - success (bool): Whether the match was successful
            - query (str): The original query
            - matched_spells (List[Dict]): List of matched spells with metadata
            - error (str, optional): Error message if match failed

        Example:
            >>> spell_sync = SpellSync()
            >>> result = spell_sync.match("How do I log out?")
            >>> result['matched_spells'][0]['name']
            'log_out_fb'
        """
        if not input_text or not isinstance(input_text, str):
            return {
                "success": False,
                "error": "Input must be a non-empty string",
                "query": input_text,
                "matched_spells": [],
            }

        try:
            spell_request = self.extract_spell_request(input_text)
            if spell_request:
                logger.info(f"Extracted spell request: {spell_request}")
                matched_spells = self.find_matching_spells(spell_request)
                if matched_spells:
                    logger.info(f"Found matching spells: {matched_spells}")
                    return {
                        "success": bool(matched_spells),
                        "query": input_text,
                        "matched_spells": matched_spells,
                    }

        except Exception as e:
            logger.error(f"Error in match(): {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": input_text,
                "matched_spells": [],
            }

    def get_spell_metadata(self, spell_name: str) -> Optional[SpellMetadata]:
        """Get spell metadata by name."""
        for spell in self.spells_data:
            if spell.name == spell_name:
                return spell
        return None

    def sync_spells(self):
        """
        Synchronizes the spells from the registry to the embeddings file.

        This method fetches all registered spells, generates embeddings for their
        docstrings, and saves the metadata to tools_embeddings.json.
        """
        logger.info("Starting spell synchronization...")

        all_spells = spell_registry.get_all_spells()
        if not all_spells:
            logger.info("No spells found in the registry. Nothing to sync.")
            return

        logger.info(f"Found {len(all_spells)} spells in the registry.")

        spells_to_sync = []
        for spell_name, spell_func in all_spells.items():
            logger.info(f"Processing spell: {spell_name}")

            docstring = spell_func.__doc__
            if not docstring:
                logger.warning(
                    f"Warning: Spell '{spell_name}' has no docstring. Skipping."
                )
                continue

            embedding = self._get_embedding(docstring)
            if embedding is None:
                logger.warning(
                    f"Warning: Could not generate embedding for '{spell_name}'. Skipping."
                )
                continue

            spell_metadata = SpellMetadata(
                name=spell_name,
                docstring=docstring,
                docstring_embedding=embedding,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            spells_to_sync.append(asdict(spell_metadata))

        tools_path = Path(__file__).parent / "tools_embeddings.json"
        logger.info(f"Writing {len(spells_to_sync)} spells to {tools_path}...")

        with open(tools_path, "w", encoding="utf-8") as f:
            json.dump(spells_to_sync, f, indent=4)

        logger.info("Spell synchronization complete.")
