"""Core Grimorium class for managing magical spells and their discovery."""

from typing import Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from . import prompts
from .spell_registry import spell_registry
from .spellsync import SpellSync
from .utils import logger


class Grimorium:
    """A magical grimoire for discovering and managing spells.

    This class provides functionality to discover, load, and manage spells
    dynamically based on semantic matching of spell descriptions.

    Args:
        connected_agent: The main agent that will use this grimorium
        model: The model to use for spell matching (default: "gemini-2.0-flash")
    """

    def __init__(
        self,
        connected_agent: Optional[Agent] = None,
        model: str = "gemini-2.0-flash",
    ):
        """Initialize the Grimorium with optional main agent and model."""
        self.connected_agent = connected_agent
        self.model = model
        self.spell_sync = SpellSync()

        if connected_agent:
            self._setup_connected_agent()

    def _setup_connected_agent(self) -> None:
        """Set up the main agent with the Grimorium tool."""
        grimorium_agent = Agent(
            name="grimorium",
            model=self.model,
            description=prompts.grimorium_description,
            instruction=prompts.grimorium_instruction,
            output_key="spell_request",
        )

        if self.connected_agent:
            logger.info(f"Adding Grimorium tool to {self.connected_agent.name}")
            self.connected_agent.tools.append(AgentTool(grimorium_agent))
            logger.info(f"Grimorium tool added to {self.connected_agent.name}")
            logger.info(f"Updating {self.connected_agent.name}'s instruction")
            self._update_instruction()
            logger.info(f"Updated {self.connected_agent.name}'s instruction")
            self.connected_agent.after_tool_callback = self._discover_best_spell
            logger.info(f"Updated {self.connected_agent.name}'s after_tool_callback")

    async def _reset_spells(self, callback_context: CallbackContext) -> None:
        """Reset the agent's tools to only include the Grimorium tool."""
        if self.connected_agent and hasattr(self.connected_agent, "tools"):
            self.connected_agent.tools = [
                tool
                for tool in self.connected_agent.tools
                if hasattr(tool, "agent") and tool.agent.name == "grimorium"
            ]

    async def _discover_best_spell(
        self,
        tool,
        args,
        tool_response,
        tool_context: ToolContext,
    ) -> types.Content:
        """Discover the best matching spell for a given request."""
        try:
            if tool.name != "grimorium":
                return tool_response
            logger.info(
                f"\nDiscovering best spell for request: {tool_context.state['spell_request']}"
            )
            result = self.spell_sync.match(tool_context.state["spell_request"])
            tool_context.state["spell_request"] = None
            if result and result["success"] and result["matched_spells"]:
                logger.debug(f"result: {result}")
                logger.debug(f"result[matched_spells]: {result['matched_spells']}")
                if not result["matched_spells"]:
                    logger.warning("No matching spells found")
                    return None

                spell_name = result["matched_spells"][0]
                logger.info(f"Found matching spell: {spell_name}")

                if spell_name and self.connected_agent:
                    # Get the function with the spell_name from the registry
                    try:
                        spell_func = spell_registry.get_spell(spell_name)
                    except KeyError:
                        logger.error(f"Error: Spell '{spell_name}' not found in registry.")
                        return f"[ERROR] Spell '{spell_name}' not found."

                    if callable(spell_func):
                        logger.info(f"Found spell function: {spell_func}")
                        self.connected_agent.tools.append(spell_func)
                        # TODO: Reset the agent's tools to only include the Grimorium tool.
                        # TODO: But when is the best time to do this?
                        # self.connected_agent.after_agent_callback = self._reset_spells
                        success_message = f"[SPELL_ADDED] {spell_name} was successfully added. You can now use {spell_name} to handle your request."
                        return success_message
            logger.warning("No matching spells found")
            return "[NO_SPELL] No suitable spell found for this request. Try rephrasing your request."
        except Exception as e:
            logger.error(f"[ERROR] An error occurred while finding a spell: {e}")
            return f"[ERROR] An error occurred while finding a spell: {e}"

    def _update_instruction(self) -> None:
        """Update the main agent's global instruction to include Grimorium usage."""
        if not self.connected_agent:
            return

        if not hasattr(self.connected_agent, "instruction"):
            self.connected_agent.instruction = ""

        self.connected_agent.instruction += prompts.grimorium_usage_guide
