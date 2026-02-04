# Getting Started with Magetools

## Installation

Install the core package:

```bash
pip install magetools
```

For full functionality (including Google GenAI and ChromaDB):

```bash
pip install magetools[full]
```

## Your First Spellbook (Grimorium)

1. **Create a tools directory**:
   ```bash
   mkdir .magetools
   ```

2. **Add a "Spell" (Tool)**:
   Create `.magetools/math_spells.py`:
   ```python
   def add_numbers(x: int, y: int) -> int:
       """Add two numbers together."""
       return x + y
   ```

3. **Initialize the Manifest**:
   Magetools requires a manifest for security:
   ```bash
   python -m magetools init .magetools
   ```

4. **Use it in Python**:
   ```python
   from magetools.grimorium import Grimorium
   import asyncio

   async def main():
       grim = Grimorium()
       await grim.initialize()
       print(f"Loaded {len(grim.registry)} tools!")

   asyncio.run(main())
   ```
