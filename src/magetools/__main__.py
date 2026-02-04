import logging

from .spellsync import SpellSync, discover_and_load_spells

logger = logging.getLogger(__name__)


def main():
    """Main entry point for Grimorium CLI."""
    logger.info("Scanning .grimorium directory for grimoriums...")

    # Discovery (loads modules and tags them)
    discover_and_load_spells()

    # Sync (buckets by tag and syncs to collections)
    spell_sync = SpellSync()
    spell_sync.sync_spells()


if __name__ == "__main__":
    main()
