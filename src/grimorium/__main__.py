import argparse
from pathlib import Path

from .spellsync import SpellSync, discover_and_load_spells
from .utils import logger


def main():
    parser = argparse.ArgumentParser(
        description="Synchronize spells for the Grimorium."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="The path (file or directory) to search for spells (default: current directory).",
    )
    args = parser.parse_args()

    logger.info(f"Discovering spells in: {Path(args.path).resolve()}")
    discover_and_load_spells(args.path)

    spell_sync = SpellSync()
    spell_sync.sync_spells()


if __name__ == "__main__":
    main()
