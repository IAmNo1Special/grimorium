"""Custom exceptions for the Grimorium system."""


class GrimoriumError(Exception):
    """Base exception for all Grimorium-related errors."""

    pass


class SpellDiscoveryError(GrimoriumError):
    """Raised when there is an error during spell discovery."""

    pass


class SpellExecutionError(GrimoriumError):
    """Raised when there is an error executing a spell."""

    pass


class ConfigurationError(GrimoriumError):
    """Raised when there is a configuration error."""

    pass


class EmbeddingError(GrimoriumError):
    """Raised when there is an error generating or processing embeddings."""

    pass
