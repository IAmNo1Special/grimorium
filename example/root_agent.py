"""Main entry point for the Grimorium example application.

This module initializes and runs the root agent with Grimorium integration,
providing an interactive command-line interface for user interaction.
"""

from __future__ import annotations

import asyncio
import logging
import sys

try:
    from dotenv import load_dotenv
    from google.adk.agents import Agent
    from google.adk.memory import InMemoryMemoryService
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    from grimorium import Grimorium
    from grimorium.utils import call_agent_async

    from . import tools
    from .config import APP_NAME, SESSION_ID, USER_ID

except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)


# Load environment variables
load_dotenv()


class _NoToolNoise(logging.Filter):
    """Filter out specific warning messages from the logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        return (
            "Warning: there are non-text parts in the response:"
            not in record.getMessage()
        )


# Configure logging
logging.basicConfig(level=logging.ERROR)
logging.getLogger("google_genai.types").addFilter(_NoToolNoise())

# Initialize the root agent
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="Root agent that coordinates with Grimorium for spell management.",
    instruction="""You are an advanced AI assistant with access to a dynamic set of capabilities.
    When a user makes a request, you can use the available tools (spells) to help them.
    If you don't have the right tool, the Grimorium system will help discover and load it.
    Be helpful, concise, and focus on solving the user's request effectively.""",
)

# Initialize Grimorium with the root agent
grimorium = Grimorium(root_agent)


async def run_root_agent() -> None:
    """Run the root agent with interactive command-line interface."""
    runner = None
    try:
        # Initialize adk services
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService()

        # Initialize session
        try:
            await session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
        except Exception as e:
            print(f"Failed to create session: {e}")
            return

        try:
            # Initialize runner
            runner = Runner(
                app_name=APP_NAME,
                agent=root_agent,
                session_service=session_service,
                memory_service=memory_service,
            )
        except Exception as e:
            print(f"Failed to create runner: {e}")
            return

        print("\n" + "=" * 60)
        print("Grimorium Interactive Shell".center(60))
        print("Type 'exit', 'quit', 'e', or 'q' to quit".center(60))
        print("=" * 60 + "\n")

        # Main interaction loop
        while True:
            query = input("You: ").strip()
            if not query:
                query = "what's the weather like today and what's my name?"
            elif query.lower() in ("exit", "quit", "e", "q"):
                break

            try:
                await call_agent_async(
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    runner=runner,
                    query=query,
                    show_function_calls=True,
                    show_function_responses=True,
                    show_inline_data=True,
                    show_state_updates=True,
                    show_artifact_updates=True,
                    show_transfer_to_agent=True,
                    show_unknown_events=True,
                    show_final_responses=True,
                )
            except Exception as e:
                print(f"Error in 'call_agent_async' call in 'run_root_agent': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":

    # Run the main async function
    try:
        asyncio.run(run_root_agent())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
