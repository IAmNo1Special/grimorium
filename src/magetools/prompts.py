grimorium_usage_guide = """

# Grimorium Usage Guide

## How to use Magic (Spells)

You have access to a Grimorium Toolset that lets you find and run python scripts ("spells").
DO NOT assume you have tools for every task. You must find them first.

### Workflow

1.  **SEARCH**: If you need to do something (e.g. "math", "check weather"), use the `magetools_search_spells` tool.
    *   Query: "calculate factorial"
2.  **ANALYZE**: Read the search results. It will give you a list of spell names.
3.  **EXECUTE**: Use the `magetools_execute_spell` tool to run the best match.
    *   Arguments: Pass the arguments required by the spell as a dictionary.

### Example

User: "What is 5! ?"
You: 
1. Call `magetools_search_spells(query="factorial")`
2. Tool Output: `{"spells": ["math_factorial"]}`
3. You Call `magetools_execute_spell(spell_name="math_factorial", arguments={"n": 5})`

"""
