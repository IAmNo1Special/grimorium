grimorium_usage_guide = """

# Grimorium Usage Guide

## How to use Magic (Spells)

You have access to a Grimorium Toolset, a vast library of tools ("spells") organized into collections ("Grimoriums").
You CANNOT search all spells at once. You must follow the Discovery Loop.

### The Discovery Loop

1.  **FIND A GRIMORIUM**: Search for a collection relevant to your high-level goal.
    *   Tool: `magetools_discover_grimoriums(query="...")`
    *   *Example: "I need to parse a CSV file" -> query="data processing"*

2.  **FIND A SPELL**: Once you have a `grimorium_id` (e.g., "data_tools"), search inside it for the specific tool.
    *   Tool: `magetools_discover_spells(grimorium_id="...", query="...")`
    *   *Example: "read csv"*

3.  **EXECUTE**: detailed_spells will give you the function signature. Run it.
    *   Tool: `magetools_execute_spell(spell_name="...", arguments={...})`

### Example Context

User: "Convert this text to speech."
You:
1. Call `magetools_discover_grimoriums(query="audio gen")` -> Returns `[{"id": "audio_ops", "desc": "..."}]`
2. Call `magetools_discover_spells(grimorium_id="audio_ops", query="text to speech")` -> Returns `{"tts_speak": "def tts_speak(text)..."}`
3. Call `magetools_execute_spell(spell_name="tts_speak", arguments={"text": "Hello"})`

"""
