"""Interfaces and Protocols for Grimorium dependency abstraction."""

from typing import Any, List, Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProviderProtocol(Protocol):
    """Protocol for embedding providers."""

    def get_embedding_function(self) -> Any:
        """Return the callable embedding function (compatible with VectorStore)."""
        ...

    def generate_content(self, prompt: str) -> str:
        """Generates text content."""
        ...


@runtime_checkable
class VectorStoreProtocol(Protocol):
    """Protocol for vector storage backends."""

    def get_collection(self, name: str, embedding_function: Any) -> Any:
        """Retrieve a collection, using the provide embedding function."""
        ...

    def list_collections(self) -> List[Any]:
        """List all available collections."""
        ...

    def get_or_create_collection(self, name: str, embedding_function: Any) -> Any:
        """Get or create."""
        ...

    # Note: We are currently leaking ChromaDB's Collection interface slightly
    # because 'get_collection' returns a Chroma Collection object.
    # To be truly abstract, we should wrap the Collection too, but that is a larger refactor.
    # For now, this Protocol abstracts the CLIENT (PersistentClient).
