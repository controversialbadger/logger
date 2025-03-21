# Prompt Enhancer

A Python script that leverages the Gemini AI API to automatically enhance user-provided prompts. The script accepts an initial prompt and utilizes Gemini to generate a revised prompt that is significantly more detailed, contextually richer, and ultimately more effective for AI models.

## Features

- Expands upon keywords in the original prompt
- Adds relevant background context
- Clarifies objectives
- Suggests diverse perspectives
- Returns enhanced prompts without explanations, lead-ins, bullet points, or surrounding quotes

## Requirements

- Python 3.7+
- Google Generative AI Python library
- Gemini API key

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your Gemini API key as an environment variable:
   ```
   export GEMINI_API_KEY='your_api_key'
   ```

## Usage

### Command Line Arguments

```
python prompt_enhancer.py --prompt "Your prompt here"
```

or

```
python prompt_enhancer.py --file path/to/prompt_file.txt
```

### Interactive Mode

If no arguments are provided, the script will enter interactive mode:

```
python prompt_enhancer.py
```

Then enter your prompt and press Ctrl+D (Unix) or Ctrl+Z (Windows) to finish input.

## Example

Input:
```
Write a story about a dragon
```

Output:
```
Write an epic fantasy tale about an ancient, wise dragon with iridescent scales who guards a forgotten library of magical knowledge beneath a dormant volcano. The dragon forms an unexpected bond with a curious scholar from a nearby village who discovers the hidden entrance. Explore their relationship as they navigate cultural misunderstandings, share knowledge across species, and eventually face a common threat from treasure hunters seeking to exploit the magical artifacts. Include details about dragon lore, the history of the magical library, and the transformation of both characters as they learn from each other's perspectives.
```