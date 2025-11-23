import argparse
import os
from dotenv import load_dotenv

from src.modules.note_linker import find_and_link_notes_with_embeddings
from src.modules.note_quality import rate_notes
from src.models.llm_clients import OllamaClient


def main():
    load_dotenv()  # Load environment variables from a .env file if present
    VAULT_DIRECTORY = os.getenv("VAULT_DIRECTORY")
    API_URL = os.getenv("API_URL")

    if not VAULT_DIRECTORY or not API_URL:
        print("Please set the VAULT_DIRECTORY and API_URL environment variables.")
        return
    try:
        ollama_client = OllamaClient(API_URL)
        print(f"Successfully connected to Ollama on url: {API_URL}")
    except Exception as e:
        print(f"Failed to connect to Ollama: {e}")
        return
    
    parser = argparse.ArgumentParser(description="A tool for managing Obsidian notes with Ollama. It can create semantic links and rate note quality.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--note-linker", action="store_true", help="Finds and links semantically similar notes.")
    group.add_argument("--note-quality", action="store_true", help="Analyzes each note and adds a quality rating and feedback.")
    args = parser.parse_args()

    if args.note_linker:
        find_and_link_notes_with_embeddings(VAULT_DIRECTORY, ollama_client)
    elif args.note_quality:
        rate_notes(VAULT_DIRECTORY, ollama_client)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
