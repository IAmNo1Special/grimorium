import inspect
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from dotenv import load_dotenv
from google import genai
from google.genai.types import EmbedContentConfig

# Add the parent directory to the path so we can import the tools module
sys.path.append(str(Path(__file__).parent.parent))

from src.grimorium import tools


def get_embedding(text: str, max_retries: int = 3) -> Optional[List[float]]:
    """
    Generate an embedding for the given text using the google genai model
    configured for semantic similarity.
    """
    load_dotenv()

    for attempt in range(max_retries):
        try:
            time.sleep(0.05)  # Avoid frequent requests
            response = genai.Client().models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
            )
            return response.embeddings[0].values
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # Exponential backoff strategy
                print(f"Error getting embedding, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                print(f"Failed to get embedding after {max_retries} attempts: {e}")
                return None


def generate_tools_json(
    tools_module: Any, output_file: str = "tools_embeddings.json"
) -> None:
    """
    Generate a JSON file containing function information and their embeddings.

    Args:
        tools_module: The module containing the tools (functions) to process
        output_file: Path to the output JSON file

    The generated JSON will have the following format:
    [
        {
            "name": "function_name",
            "docstring": "Function docstring",
            "docstring_embedding": [list of floats]
        },
        ...
    ]
    """
    # Get all functions from the tools module
    functions = [
        obj
        for name, obj in sorted(inspect.getmembers(tools_module))
        if (
            inspect.isfunction(obj)
            and obj.__module__ == tools_module.__name__
            and not name.startswith("_")
        )  # Skip private functions
    ]

    tools_data = []

    for func in functions:
        # Get function name
        func_name = func.__name__

        # Get function docstring
        docstring = inspect.getdoc(func) or ""
        # Clean up the docstring by removing extra whitespace
        docstring = "".join(line.strip() for line in docstring.split("\n")).strip()

        # Skip if no docstring
        if not docstring:
            continue

        # Get embedding for the docstring
        embedding = get_embedding(docstring)

        if embedding is not None:
            tools_data.append(
                {
                    "name": func_name,
                    "docstring": docstring,
                    "created_at": datetime.now().isoformat(),
                    "docstring_embedding": embedding,
                }
            )

    # Write to JSON file
    with open(output_file, "w") as f:
        json.dump(tools_data, f, indent=2)

    print(f"Successfully generated {output_file} with {len(tools_data)} tools")


def main():
    # Generate the tools JSON file
    output_file = "tools_embeddings.json"
    generate_tools_json(tools, output_file)
    print(f"Tools JSON file generated at: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    main()
