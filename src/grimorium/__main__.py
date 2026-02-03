import argparse
import logging
from pathlib import Path

from .spellsync import SpellSync
from .utils import discover_and_load_spells

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Synchronize spells for the Grimorium."
    )
    parser.add_argument(
        "--path",
        "-p",
        type=str,
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