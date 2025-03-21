#!/usr/bin/env python3

import os
import sys
import argparse
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument

def setup_gemini_api():
    """Set up and configure the Gemini API client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set your API key with: export GEMINI_API_KEY='your_api_key'")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

def enhance_prompt(model, original_prompt):
    """
    Use Gemini to enhance the original prompt by making it more detailed,
    contextually rich, and effective.
    """
    system_instruction = """
    You are a prompt enhancement specialist. Your task is to transform the user's 
    initial prompt into a significantly more detailed, contextually rich, and effective prompt.
    
    Enhance the original prompt by:
    - Expanding upon keywords
    - Adding relevant background context
    - Clarifying objectives
    - Suggesting diverse perspectives
    
    IMPORTANT: Your response must ONLY contain the enhanced prompt itself.
    DO NOT include:
    - Any explanations or lead-in text
    - Bullet points
    - Placeholders
    - Surrounding quotes
    - Any conversation or meta-commentary
    
    Just return the enhanced prompt text directly.
    """
    
    try:
        response = model.generate_content(
            [
                {"role": "system", "parts": [system_instruction]},
                {"role": "user", "parts": [original_prompt]}
            ],
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
            }
        )
        
        # Extract just the text content
        enhanced_prompt = response.text.strip()
        return enhanced_prompt
    
    except InvalidArgument as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Enhance prompts using Gemini AI")
    parser.add_argument("--prompt", type=str, help="The prompt to enhance")
    parser.add_argument("--file", type=str, help="File containing the prompt to enhance")
    args = parser.parse_args()
    
    # Get the prompt from either command line argument or file
    if args.prompt:
        original_prompt = args.prompt
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                original_prompt = f.read().strip()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
    else:
        # If no arguments provided, read from stdin
        print("Enter your prompt (Ctrl+D to finish):")
        original_prompt = sys.stdin.read().strip()
    
    if not original_prompt:
        print("Error: No prompt provided.")
        sys.exit(1)
    
    # Set up the Gemini API and enhance the prompt
    model = setup_gemini_api()
    enhanced_prompt = enhance_prompt(model, original_prompt)
    
    # Output the enhanced prompt directly without any additional text
    print(enhanced_prompt)

if __name__ == "__main__":
    main()