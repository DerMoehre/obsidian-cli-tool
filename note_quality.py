import requests
import json
import re
import time
import os
import yaml

def get_note_rating_from_ollama(text, model_name="llama3"):
    """
    Sends a note's content to a language model to get a rating and feedback.
    The model is instructed to respond in a structured JSON format.

    Args:
        text (str): The text content of the note to rate.
        model_name (str): The name of the Ollama language model to use.

    Returns:
        dict: A dictionary containing the rating and suggestions, or an empty dict on failure.
    """
    url = "http://localhost:11434/api/generate"

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
    payload = {
        "model": model_name,
        "prompt": RATING_PROMPT_TEMPLATE,
        "stream": False,
        "options": {
            "temperature": 0.0 # Use a low temperature for more deterministic output
        }
    }

    try:
        print(f"  > Getting rating from Ollama using model '{model_name}'...")
        response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        
        rating_result = json.loads(response.text)
        
        if "response" in rating_result:
            json_str = rating_result["response"]
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            rating_data = json.loads(json_str)
            if "rating" in rating_data and "feedback" in rating_data:
                print(f"  > Received rating: {rating_data['rating']} and feedback: {rating_data['feedback']}")
                return rating_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama server: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Ollama: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return {}
    
def rate_notes(vault_path: str, ollama_model_name:str = "llama3"):
    """
    Analyzes each note in the vault, gets a rating from an LLM, and adds
    a 'Note Quality' section with the rating and feedback.

    Args:
        vault_path (str): The absolute path to your Obsidian vault directory.
        ollama_model_name (str): The name of the Ollama language model to use.
    """
    for root, _, files in os.walk(vault_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                print(f"Processing note: {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Get the rating from Ollama
                rating_result = get_note_rating_from_ollama(content, ollama_model_name)
                
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