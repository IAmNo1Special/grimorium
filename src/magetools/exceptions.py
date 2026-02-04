"""Custom exceptions for the Magetools system."""


class MagetoolsError(Exception):
    """Base exception for all Magetools-related errors."""

    pass


class SpellDiscoveryError(MagetoolsError):
    """Raised when there is an error during spell discovery."""

    pass


class SpellExecutionError(MagetoolsError):
    """Raised when there is an error executing a spell."""

    pass


class SpellAccessDeniedError(MagetoolsError):
    """Raised when access to a spell is denied due to collection restrictions."""

    pass


class ConfigurationError(MagetoolsError):
    """Raised when there is a configuration error or missing dependency."""

    pass


class EmbeddingError(MagetoolsError):
    """Raised when there is an error generating or processing embeddings."""

    pass


class QuarantineError(SpellDiscoveryError):
    """Raised when a spell file is quarantined due to import failures."""

    pass


# Backwards compatibility aliases
GrimoriumError = MagetoolsError
