import requests
import json
import re
import time
import os
import yaml

def get_note_rating_from_ollama(text: str, ollama_client) -> dict:
    """
    Sends a note's content to a language model to get a rating and feedback.
    The model is instructed to respond in a structured JSON format.

    Args:
        text (str): The text content of the note to rate.
        model_name (str): The name of the Ollama language model to use.

    Returns:
        dict: A dictionary containing the rating and suggestions, or an empty dict on failure.
    """

    RATING_PROMPT_TEMPLATE = f"""You are a meticulous note-taking assistant. Your task is to rate the quality of a given Markdown note based on two criteria: information density and completeness. The rating should be on a scale from 1 to 10. You will also provide a single, actionable piece of feedback for improvement.

    The output must be a single JSON object with two keys:
    1. "rating": The numerical rating (1-10).
    2. "feedback": A concise string with one suggestion for improvement.

    For example, if a note is very detailed, you might return:
    {{
    "rating": 9,
    "feedback": "Add an example or case study to illustrate the concepts."
    }}

    Here is the note to rate. Provide only the JSON object in your response.

    ---
    Note content:
    {text}
    """

    try:
        print(f"  > Getting rating from Ollama ...")
        raw_response = ollama_client.generate(
            prompt=RATING_PROMPT_TEMPLATE, 
            json_mode=True 
        )

        if not raw_response:
            print("  > No response from Ollama.")
            return {}
                
        try:
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]

            rating_data = json.loads(raw_response.strip())

            if "rating" in rating_data and "feedback" in rating_data:
                print(f"  > Rating: {rating_data['rating']} and feedback.")
                return rating_data
            else:
                print(f"Did not receive a valid JSON format from model: {rating_data}")
                return {}
        except json.JSONDecodeError as e:
            print(f"Error on parsing the JSON response of Ollama: {e}")
            return {}
        except Exception as e:
            print(f"An unexpected error occured while parsing the answer: {e}")
            return {}
        
    except Exception as e:
        print(f"An unexpected error occured while getting rating from Ollama: {e}")
        return {}
    
def rate_notes(vault_path: str, ollama_client):
    """
    Analyzes each note in the vault, gets a rating from an LLM, and adds
    a 'Note Quality' section with the rating and feedback.

    Args:
        vault_path (str): The absolute path to your Obsidian vault directory.
        ollama_client: Initialised ollama client.
    """
    for root, _, files in os.walk(vault_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                print(f"Processing note: {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Get the rating from Ollama
                rating_result = get_note_rating_from_ollama(content, ollama_client)
                
                if rating_result:
                    rating = rating_result.get("rating")
                    feedback = rating_result.get("feedback")
                    
                    # Split the content to find the YAML frontmatter
                    yaml_match = re.search(r"^---\s*\n(?P<yaml_content>.*?)\n---\s*\n", content, re.DOTALL)
                    
                    if yaml_match:
                        # An existing YAML block was found
                        yaml_data = yaml.safe_load(yaml_match.group("yaml_content")) or {}
                        
                        if "rating" in yaml_data:
                            print("  > Note already has a rating in the frontmatter. Skipping.\n")
                            continue
                        
                        yaml_data["rating"] = rating
                        yaml_data["feedback"] = feedback
                        
                        updated_yaml_str = yaml.safe_dump(yaml_data, sort_keys=False)
                        
                        # Re-assemble the content with the updated YAML
                        new_content = f"---\n{updated_yaml_str}---\n{content[yaml_match.end():]}"
                    else:
                        # No existing YAML block, create a new one
                        new_yaml_block = f"---\nrating: {rating}\nfeedback: {feedback}\n---\n"
                        new_content = new_yaml_block + content
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"  > Added rating to {file}\n")
                else:
                    print(f"  > Failed to get rating for {file}, skipping.\n")