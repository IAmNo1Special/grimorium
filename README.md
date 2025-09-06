# Grimorium

A magical Python library for dynamically discovering, loading, and managing "spells" (Python functions) using semantic matching. Grimorium allows you to build extensible AI agents that can discover and use new capabilities at runtime.

## Features

- **Dynamic Spell Discovery**: Automatically find and load functions based on natural language descriptions
- **Semantic Matching**: Uses embeddings to match spell descriptions to user intents
- **Decorator-based API**: Simple `@spell` decorator to make any function discoverable
- **Type Annotations**: Full support for Python type hints
- **Async Support**: Native support for both synchronous and asynchronous spells
- **Versioning**: Track and manage different versions of spells
- **Tagging**: Organize spells with tags for better discoverability

## Installation

Grimorium requires Python 3.9+ and can be installed using `uv`:

```bash
# Install grimorium with uv
uv add grimorium
```

or

```bash
# Install grimorium with pip
pip install grimorium
```

## Quick Start

### Create a Spell

```python
from grimorium import spell

@spell(version="1.0.0", tags=["weather", "api"])
async def get_weather(location: str, unit: str = 'celsius') -> str:
    """Get the current weather for a given location.
    
    Args:
        location: City or location to get weather for
        unit: Temperature unit ('celsius' or 'fahrenheit')
        
    Returns:
        String describing the current weather
    """
    # Implementation here
    return f"The weather in {location} is 22°{unit[0].upper()}"
```

1. **Discover and use spells**:

```python
from grimorium import Grimorium

# Initialize Grimorium
grimorium = Grimorium()

# Discover spells matching a description
result = grimorium.spell_sync.match("What's the weather like in Paris?")
if result["success"] and result["matched_spells"]:
    spell = result["matched_spells"][0]
    weather = await spell["function"](location="Paris")
    print(weather)
```

## Core Concepts

### Spells

A "spell" is simply a Python function decorated with `@spell`. Spells can be:

- Synchronous or asynchronous
- Typed with Python type hints
- Versioned and tagged
- Discovered via natural language queries

### Grimorium Class

The `Grimorium` class is the main entry point that provides:

- Spell discovery and management
- Integration with AI agents
- Semantic search capabilities

### SpellSync

`SpellSync` handles the low-level spell registration and matching:

- Maintains a registry of all available spells
- Uses semantic embeddings for matching
- Handles versioning and metadata

## Advanced Usage

### Auto-discovery of Spells

Place your spell modules in a `grimorium/spells/` directory, and they'll be automatically discovered:

```text
your_project/
├── grimorium/
│   └── spells/
│       ├── __init__.py
│       ├── weather.py
│       └── calculator.py
└── main.py
```

### Using with AI Agents

Grimorium works seamlessly with AI agents to dynamically extend their capabilities:

```python
from google.adk.agents import Agent
from grimorium import Grimorium

# Create an AI agent
agent = Agent(
    name="magical_assistant",
    model="gemini-2.0-flash",
    description="An AI assistant with magical abilities"
)

# Initialize Grimorium with the agent
grimorium = Grimorium(agent)

# The agent can now use any registered spell
response = await agent.run("What's the weather like in Tokyo?")
```

### Configuration

Configure Grimorium using environment variables:

```bash
# Required: Set your Google API key for embeddings
GOOGLE_API_KEY=your_api_key_here

# Optional: Customize the embedding model
GRIMORIUM_MODEL=gemini-2.0-flash
```

## API Reference

### @spell Decorator

```python
@spell(
    name: str,
    description: str,
    version: str = "1.0.0",
    tags: List[str] = None,
    spell_type: str = "sync"  # or "async"
)
```

### Grimorium Class Reference

```python
class Grimorium:
    def __init__(self, main_agent: Optional[Agent] = None, model: str = "gemini-2.0-flash"):
        ...
    
    async def discover_spell(self, query: str) -> Dict[str, Any]:
        """Find the best matching spell for a natural language query."""
        ...
```

## Development

### Development Environment Setup

1. Clone the repository
2. Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
uv pip install -e ".[docs]"
mkdocs serve
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
