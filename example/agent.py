"""Main entry point for the Grimorium example application.

This module initializes and runs the root agent with Grimorium integration,
providing an interactive command-line interface for user interaction.
"""

from __future__ import annotations

import asyncio
import logging
import sys

import tools
from config import APP_NAME, SESSION_ID, USER_ID
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from grimorium import Grimorium
from grimorium.utils import call_agent_async

# Load environment variables
load_dotenv()


class _NoToolNoise(logging.Filter):
    """Filter out specific warning messages from the logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        return (
            "Warning: there are non-text parts in the response:"
            not in record.getMessage()
        )


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger("google_genai.types").addFilter(_NoToolNoise())

# Initialize the root agent
root_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    description="Agent that help the user.",
    instruction="""You are an advanced AI assistant.
    Be helpful, concise, and focus on solving the user's request effectively.""",
)

# Initialize Grimorium with the root agent
Grimorium(connected_agent=root_agent)


async def run_grimorium_agent() -> None:
    """Run the root agent with interactive command-line interface."""
    runner = None
    try:
        # Initialize adk services
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService()

        # Initialize session
        try:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
            )
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
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
            logger.error(f"Failed to create runner: {e}")
            return

        logger.info("\n" + "=" * 60)
        logger.info("Grimorium Interactive Shell".center(60))
        logger.info("Type 'exit', 'quit', 'e', or 'q' to quit".center(60))
        logger.info("=" * 60 + "\n")

        # Main interaction loop
        while True:
            query = input("You: ").strip()
            if query.lower() in ("exit", "quit", "e", "q"):
                break
            center_width = 60
            logger.info("\n")
            logger.info(
                f" [User]>>>[QUERY]>>>[{runner.agent.name}] ".center(center_width, "=")
            )

            if not query:
                query = "what's the weather like today and what's my name?"
                logger.info(f"Default Query: {query}")
            logger.info("=" * center_width)

            try:
                await call_agent_async(
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    runner=runner,
                    query=query,
                    show_function_calls=True,
                    show_function_responses=True,
                    show_final_responses=True,
                )
            except Exception as e:
                logger.error(f"Error in 'call_agent_async' call in 'run_root_agent': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":

    # Run the main async function
    try:
        asyncio.run(run_grimorium_agent())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
