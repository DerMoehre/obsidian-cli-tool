import requests
from typing import List

class OllamaClient:
    """
    A client to interact with a local Ollama instance for generating embeddings.
    """
    def __init__(self, api_base_url: str):
        """
        Initializes the OllamaClient with the base URL of the Ollama instance.

        Args:
            api_base_url (str): The base url of the ollama client (e.g. "http://localhost:11434").
        """
        self.api_base_url = api_base_url.rstrip('/')

    def get_embedding(self, text: str, model_name: str = "nomic-embed-text") -> List[float]:
        """
        Takes a text input and returns its vector embedding using the specified Ollama model.

        Args:
            text (str): The text that the user wants to be embedded.
            model_name (str): The name of the used model.

        Returns:
            List[float]: A list of floats representing the vector embedding or an empty list on failure.
        """
        url = f"{self.api_base_url}/api/embeddings" 
        
        payload = {
            "model": model_name,
            "prompt": text,
            "stream": False 
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            return data.get("embedding", [])
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP-error on connection with Ollama: {e}")
            print(f"Details: {response.text}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error on connection with Embedding: {e}")
            print("Make sure the embedding model is pulled and Ollama is running.")
            return []
        except Exception as e:
            print(f"An unexpected error occured: {e}")
            return []
        
    def generate(self, prompt: str, model_name: str = "llama3", system_prompt: str = None, json_mode: bool = False) -> str | None:
        """
        Send a prompt to the Ollama LLM and get the generated response.

        Args:
            model_name (str):Name of the used LLM (e.g. "llama3").
            prompt (str): Main prompt.
            system_prompt (str, optional): optional system prompt.
            json_mode (bool, optional): formats answer to JSON format.

        Returns:
            str | None: Raw answer of the model or non if an error occurs.
        """
        url = f"{self.api_base_url}/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0 # Use a low temperature for more deterministic output
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt 
        
        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()

            return data.get("response")
            
        except requests.exceptions.RequestException as e:
            print(f"Error on generating answer: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occured: {e}")
            return None