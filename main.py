import argparse
import os
from dotenv import load_dotenv

from note_linker import find_and_link_notes_with_embeddings
from note_quality import rate_notes


def main():
    load_dotenv()  # Load environment variables from a .env file if present
    try:
        VAULT_DIRECTORY = os.getenv("VAULT_DIRECTORY")
    except KeyError:
        print("Error: VAULT_DIRECTORY environment variable not set.")
        return
    vault_directory = VAULT_DIRECTORY  # Change this to your vault path
    parser = argparse.ArgumentParser(description="A tool for managing Obsidian notes with Ollama. It can create semantic links and rate note quality.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--note-linker", action="store_true", help="Finds and links semantically similar notes.")
    group.add_argument("--note-quality", action="store_true", help="Analyzes each note and adds a quality rating and feedback.")
    args = parser.parse_args()

    if args.note_linker:
        find_and_link_notes_with_embeddings(vault_directory)
    elif args.note_quality:
        rate_notes(vault_directory)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
