"""Core Grimorium class for managing magical spells and their discovery."""

from typing import Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from . import prompts
from .spellsync import SpellSync
from .spell_registry import spell_registry


class Grimorium:
    """A magical grimoire for discovering and managing spells.

    This class provides functionality to discover, load, and manage spells
    dynamically based on semantic matching of spell descriptions.

    Args:
        main_agent: The main agent that will use this grimoire
        model: The model to use for spell matching (default: "gemini-2.0-flash")
    """

    def __init__(
        self,
        main_agent: Optional[Agent] = None,
        model: str = "gemini-2.0-flash",
    ):
        """Initialize the Grimorium with optional main agent and model."""
        self.main_agent = main_agent
        self.model = model
        self.spell_sync = SpellSync()

        if main_agent:
            self._setup_main_agent()

    def _setup_main_agent(self) -> None:
        """Set up the main agent with the Grimorium tool."""
        grimorium_agent = Agent(
            name="grimorium",
            model=self.model,
            description=prompts.grimorium_description,
            instruction=prompts.grimorium_instruction,
            output_key="spell_request",
        )

        if self.main_agent:
            print("1. This should only run once. run #1")
            print(self.main_agent.tools)
            self.main_agent.tools.append(AgentTool(grimorium_agent))
            print("2. This should only run once. run #1")
            print(self.main_agent.tools)
            self._update_instruction()
            self.main_agent.after_tool_callback = self._discover_best_spell

    async def _reset_spells(self, callback_context: CallbackContext) -> None:
        """Reset the agent's tools to only include the Grimorium tool."""
        if self.main_agent and hasattr(self.main_agent, "tools"):
            self.main_agent.tools = [
                tool
                for tool in self.main_agent.tools
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
            print(
                f"\nDiscovering best spell for request: {tool_context.state['spell_request']}"
            )
            result = self.spell_sync.match(tool_context.state["spell_request"])
            if result and result["success"] and result["matched_spells"]:
                print("result", result)
                tool_context.state["spell_request"] = None
                print("result[matched_spells]", result["matched_spells"])
                if not result["matched_spells"]:
                    print("No matching spells found")
                    return None
                    
                spell_name = result["matched_spells"][0]
                print(f"Found matching spell: {spell_name}")
                
                if spell_name and self.main_agent:
                    # Get the function with the spell_name from the registry
                    try:
                        spell_func = spell_registry.get_spell(spell_name)
                    except KeyError:
                        print(f"Error: Spell '{spell_name}' not found in registry.")
                        return self._create_error_response(
                            f"[ERROR] Spell '{spell_name}' not found."
                        )

                    if callable(spell_func):
                        print(f"Found spell function: {spell_func}")
                        self.main_agent.tools.append(spell_func)
                        # TODO: Reset the agent's tools to only include the Grimorium tool.
                        # TODO: But when is the best time to do this?
                        # self.main_agent.after_agent_callback = self._reset_spells

                        return types.Content(
                            role="model",
                            parts=[
                                types.Part.from_text(
                                    text=f"[SPELL_ADDED] Successfully added: {spell_name}"
                                )
                            ],
                        )
            return self._create_error_response(
                "[NO_SPELL] No suitable spell found for this request. "
                "Try rephrasing your request."
            )
        except Exception as e:
            return self._create_error_response(
                f"[ERROR] An error occurred while finding a spell: {e}"
            )

    def _update_instruction(self) -> None:
        """Update the main agent's global instruction to include Grimorium usage."""
        if not self.main_agent:
            return

        if not hasattr(self.main_agent, "instruction"):
            self.main_agent.instruction = ""

        self.main_agent.instruction += prompts.grimorium_usage_guide

    @staticmethod
    def _create_error_response(message: str) -> types.Content:
        """Create an error response content."""
        return types.Content(role="model", parts=[types.Part.from_text(text=message)])
