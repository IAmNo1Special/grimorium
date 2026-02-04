"""Adapters for Grimorium."""

from typing import Any, List

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google import genai

from .interfaces import EmbeddingProviderProtocol, VectorStoreProtocol

load_dotenv()


class GoogleGenAIProvider(EmbeddingProviderProtocol):
    """Provider for Google Generative AI embeddings."""

    def get_embedding_function(self) -> Any:
        return embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            task_type="SEMANTIC_SIMILARITY"
        )

    def generate_content(self, prompt: str) -> str:
        """Generates content using Google Gemini model."""

        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        return response.text


class ChromaVectorStore(VectorStoreProtocol):
    """Adapter for ChromaDB."""

    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(path=str(path))

    def get_collection(self, name: str, embedding_function: Any) -> Any:
        return self.client.get_collection(
            name=name, embedding_function=embedding_function
        )

    def list_collections(self) -> List[Any]:
        return self.client.list_collections()

    def get_or_create_collection(self, name: str, embedding_function: Any) -> Any:
        return self.client.get_or_create_collection(
            name=name, embedding_function=embedding_function
        )
