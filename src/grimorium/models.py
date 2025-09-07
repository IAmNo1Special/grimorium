from dataclasses import dataclass
from typing import List


@dataclass
class SpellMetadata:
    """Comprehensive metadata for a registered spell."""

    name: str
    docstring: str
    created_at: str
    docstring_embedding: List[float]
