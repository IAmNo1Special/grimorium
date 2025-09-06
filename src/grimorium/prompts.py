grimorium_description = """
# Grimorium - Magical Spell Management System

## Overview
The Grimorium is a dynamic spell management system that automatically discovers and loads the most appropriate spells (tools) based on the user's request using semantic matching.

## How It Works

### 1. Automatic Spell Discovery
- When a user makes a request, the Grimorium analyzes it using semantic matching
- The system finds the most relevant spell from the available collection
- The matching spell is automatically added to your available tools

### 2. Response Handling
- On successful spell addition:
  ```
  [SPELL_ADDED] Successfully added: [spell_name]
  ```
- If no matching spell is found:
  ```
  [NO_SPELL] No suitable spell found for this request. Try rephrasing your request.
  ```
- On error:
  ```
  [ERROR] An error occurred while finding a spell: [error_details]
  ```

### 3. Spell Usage
- The spell is immediately available in your toolset after being added
- The Grimorium automatically resets between requests, so each new request starts fresh

## Implementation Details
- Uses semantic matching to find the most relevant spell
- Spells are dynamically loaded and unloaded as needed
- The system is designed to be self-contained and requires minimal configuration
- Works with the main agent system through a clean integration point

## Best Practices
- Keep spell descriptions clear and focused for better matching
- Handle cases where no matching spell is found gracefully
- Implement proper error handling for spell discovery and loading
- Consider the context of the request when determining the most appropriate spell
"""

grimorium_instruction = """# Grimorium Spell Identification

## Objective
Your task is to identify the specific **SPELL** (tool/function/capability) that would
best address the user's request.

## Instructions

### Analysis Process
1. **Read Carefully**: Thoroughly understand the user's request
2. **Identify Requirements**: Determine the key requirements and intentions
3. **Determine Spell**: Identify the specific spell(tool/function/capability) (SPELL) needed

### Response Format
Respond using ONLY the following format:

<spell_request>
    spell: [brief description of the spell/function from user's request]
</spell_request>

## Guidelines
- Be **concise** but **descriptive**
- Include **only** the spell(tool/function/capability) description within the `<spell_request>` tags
- **Do not** include any additional explanation or commentary outside the tags
- Keep the description focused on the **core functionality** of the requested spell(tool/function/capability)
"""

grimorium_usage_guide = """# Grimorium Usage Guide

## Overview
This guide explains how to use the Grimorium tool to find and load the necessary
spells (tools/functions/capabilities) to complete user requests.

## Instructions

### Step 1: Identify Missing Capabilities
- When you encounter a request you can't fulfill:
  - Analyze what specific capability is missing
  - Assume it's a spell(tool/function/capability) that can be loaded from the grimorium

### Step 2: Requesting a Spell
- Be **specific** and **clear** in your request
- Use the format:
  ```
  I need a spell to [specific action]
  ```
- Example requests:
  - "I need a spell to get the current weather."
  - "I need a spell to get the user's name."
  - "I need a spell to log the user out of Facebook."

### Step 3: Using the Spell
- The Grimorium will attempt to load the requested spell(tool/function/capability)
- Once loaded, you can use it immediately
- For multiple spells(tool/functions/capabilities), request them one at a time

## Best Practices
- **Be specific**: Clearly describe the exact functionality needed
- **One at a time**: Request spells(tool/functions/capabilities) individually for better tracking
- **Verify functionality**: Ensure the loaded spell(tool/function/capability) meets the requirements
- **Error handling**: Be prepared to handle cases where a spell(tool/function/capability) isn't available

> **Remember**: Clear and specific requests yield better results!
"""
