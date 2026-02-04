"""Core Grimorium toolset for managing magical spells and their discovery."""

import asyncio
import inspect
import logging
from typing import Any, List, Optional

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import BaseTool, FunctionTool, ToolContext
from google.adk.tools.base_toolset import BaseToolset

from .prompts import grimorium_usage_guide
from .spellsync import SpellSync, discover_and_load_spells

logger = logging.getLogger(__name__)


class Grimorium(BaseToolset):
    """A magical grimoire toolset for discovering and managing spells.
    This toolset provides two main tools:
    1. magetools_search_spells: To find available spells.
    2. magetools_execute_spell: To run a specific spell.
    """

    def __init__(
        self,
        root_path: Optional[str] = None,
        allowed_collections: Optional[List[str]] = None,
        embedding_provider: Any = None,  # Use Any to avoid circular import or define Protocol
        vector_store: Any = None,
    ):
        """Initialize the Grimorium toolset.

        Args:
            root_path: Optional path string to the project root.
            allowed_collections: Optional list of collection names.
            embedding_provider: Optional EmbeddingProviderProtocol implementation.
            vector_store: Optional VectorStoreProtocol implementation.
        """
        # Initialize the base toolset with a prefix to avoid naming collisions
        super().__init__(tool_name_prefix="magetools")

        import inspect
        from pathlib import Path

        path_obj = None

        if root_path:
            path_obj = Path(root_path)
        else:
            # Magic: Auto-detect the caller's frame to find where Grimorium is instantiated
            try:
                # Stack[0] is here, Stack[1] is the caller
                frame = inspect.stack()[1]
                caller_file = frame.filename
                if caller_file:
                    path_obj = Path(caller_file).parent.resolve()
                    logger.debug(
                        f"Auto-detected Grimorium root from caller: {path_obj}"
                    )
            except Exception as e:
                logger.warning(f"Could not auto-detect caller path: {e}")

        # Fallback to CWD if magic failed and no path provided
        if not path_obj:
            path_obj = Path.cwd()

        self.spell_sync = SpellSync(
            root_path=path_obj,
            allowed_collections=allowed_collections,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )

        # Always discover and load spells from the computed root
        logger.debug(
            f"Initializing Grimorium with root: {self.spell_sync.MAGETOOLS_ROOT}"
        )
        discover_and_load_spells(
            self.spell_sync.MAGETOOLS_ROOT, registry=self.spell_sync.registry
        )
        self.spell_sync.sync_spells()
        # Create the tools that will be exposed to the agent
        self._search_spells_tool = FunctionTool(func=self.search_spells)
        self._execute_spell_tool = FunctionTool(func=self.execute_spell)
        logger.debug("Grimorium initialized successfully.")

    @property
    def usage_guide(self) -> str:
        """Returns the usage guide instructions for using this toolset."""
        return grimorium_usage_guide

    def search_spells(self, query: str) -> dict[str, Any]:
        """Search for spells that match a given description.

        Args:
            query: A description of the spell or functionality you are looking for.
                   Example: "calculate factorial" or "send email"
        Returns:
            A dictionary containing the search results and metadata of found spells.
        """
        logger.debug(f"Grimorium searching for: {query}...")
        result = self.spell_sync.find_matching_spells(query)

        if result:
            spell_names = result
            detailed_spells = {}

            for name in spell_names:
                try:
                    func = self.spell_sync.registry[name]
                    sig = inspect.signature(func)
                    # Get docstring but clean it up a bit (first line or summary)
                    doc = inspect.getdoc(func) or "No description available."

                    detailed_spells[name] = {
                        "description": doc,
                        "signature": str(sig),
                    }
                except Exception as e:
                    logger.warning(f"Could not inspect spell {name}: {e}")
                    detailed_spells[name] = {"error": "Details unavailable"}

            logger.debug(f"Found spells: {spell_names}")
            return {
                "status": "success",
                "message": f"Found {len(spell_names)} potential spells.",
                "spells": detailed_spells,
                "hint": "Use 'magetools_execute_spell' with the exact name of one of these spells and the required arguments from the signature.",
            }

        logger.debug("No spells found matching that description.")
        return {
            "status": "not_found",
            "message": "No spells found matching that description. Try a different query.",
        }

    async def execute_spell(
        self, spell_name: str, arguments: dict[str, Any], tool_context: ToolContext
    ) -> dict[str, Any]:
        """Execute a specific spell by name.
        Args:
            spell_name: The exact name of the spell to find and execute.
            arguments: A dictionary of arguments to pass to the spell function.
        Returns:
            The result of the spell execution.
        """
        logger.info(
            f"Grimorium executing spell: {spell_name} with args: {arguments}..."
        )

        try:
            # SECURITY CHECK: Verify spell is allowed for this instance
            if not self.spell_sync.validate_spell_access(spell_name):
                return {
                    "status": "error",
                    "message": f"Permission denied: Spell '{spell_name}' is not in your allowed collections.",
                }

            spell_func = self.spell_sync.registry[spell_name]
        except KeyError:
            return {
                "status": "error",
                "message": f"Spell '{spell_name}' not found. Did you search for it first?",
            }
        try:
            # Check if the target spell function expects 'tool_context'
            sig = inspect.signature(spell_func)

            # Use a copy to avoid mutating the original arguments
            call_args = arguments.copy()

            # Robust injection of context by Type and Name
            for name, param in sig.parameters.items():
                if param.annotation == ToolContext:
                    call_args[name] = tool_context
                elif name == "tool_context" and name not in call_args:
                    call_args[name] = tool_context

            # Execute the spell with the prepared arguments
            if inspect.iscoroutinefunction(spell_func):
                result = await spell_func(**call_args)
            else:
                # Run sync functions in a separate thread to keep the loop alive
                result = await asyncio.to_thread(spell_func, **call_args)

            return {"status": "success", "result": result}

        except TypeError as te:
            logger.error(f"Argument mismatch for spell {spell_name}: {te}")
            return {
                "status": "error",
                "message": f"Failed to call spell. Please check arguments. details: {str(te)}",
            }
        except Exception as e:
            logger.error(f"Error executing spell {spell_name}: {e}")
            return {"status": "error", "message": f"Execution failed: {str(e)}"}

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        """Return the list of tools provided by this toolset."""
        return [self._search_spells_tool, self._execute_spell_tool]
