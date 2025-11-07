import time
import requests
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_embedding_from_ollama(text:str, model_name="nomic-embed-text")->list:
    """
    Sends text to a local Ollama instance to get its vector embedding.
    Args:
        text (str): The text content to embed.
        model_name (str): The name of the Ollama embedding model to use.

    Returns:
        list: A list of floats representing the vector embedding.
    """
    url = "http://localhost:11434/api/embeddings"
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
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama for embedding: {e}")
        print("Please ensure Ollama is running and the embedding model is pulled.")
        return []

def find_and_link_notes_with_embeddings(vault_path:str, ollama_model_name="nomic-embed-text"):
    """
    Scans an Obsidian vault, calculates embeddings for each note, and
    automatically links the most semantically similar notes.

    Args:
        vault_path (str): The absolute path to your Obsidian vault directory.
        ollama_model_name (str): The name of the Ollama embedding model to use.
    """
    print(f"Scanning vault at: {vault_path}")

    # --- Step 1: Gather notes and their content ---
    all_notes = []
    for root, _, files in os.walk(vault_path):
        for file in files:
            if file.endswith('.md'):
                note_path = os.path.join(root, file)
                title = os.path.basename(note_path)[:-3]
                try:
                    with open(note_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    all_notes.append({
                        "title": title,
                        "path": note_path,
                        "content": content
                    })
                except Exception as e:
                    print(f"Could not read file {note_path}: {e}")
                    continue

    if not all_notes:
        print("No Markdown files found. Please check the vault path.")
        return

    # --- Step 2: Generate embeddings for all notes ---
    print("\nGenerating embeddings for all notes...")
    note_embeddings = []
    for note in all_notes:
        embedding = get_embedding_from_ollama(note["content"], model_name=ollama_model_name)
        if embedding:
            note_embeddings.append({
                "title": note["title"],
                "path": note["path"],
                "embedding": np.array(embedding)
            })
        time.sleep(0.5) # Add a small delay to avoid overwhelming the API

    if not note_embeddings:
        print("No embeddings were generated. Exiting.")
        return

    linked_count = 0
    
    # --- Step 3: Find and link semantically similar notes ---
    # Convert embeddings to a single NumPy array for efficient calculation
    embeddings_matrix = np.array([item["embedding"] for item in note_embeddings])
    
    # Calculate the cosine similarity matrix for all notes
    similarity_matrix = cosine_similarity(embeddings_matrix)

    # We will use a threshold to decide if notes are similar enough to link.
    SIMILARITY_THRESHOLD = 0.7
    
    # Iterate through each note to find its best matches
    for i, source_note in enumerate(note_embeddings):
        source_title = source_note["title"]
        source_path = source_note["path"]
        
        # Get the similarity scores for the current note
        similarity_scores = similarity_matrix[i]
        
        # Get the indices of the notes sorted by similarity (descending)
        # starting from index 1 to skip the note itself
        sorted_indices = np.argsort(similarity_scores)[::-1][1:]
        
        # Find the top N most similar notes, excluding the source note
        top_matches = []
        for j in sorted_indices:
            # Skip the note if it's the same as the source note
            if i == j:
                continue
            
            target_note = note_embeddings[j]
            similarity = similarity_scores[j]
            
            # Check if the similarity is above our threshold
            if similarity > SIMILARITY_THRESHOLD:
                top_matches.append((target_note, similarity))
            
            # Stop if we have enough matches (e.g., top 3)
            if len(top_matches) >= 3:
                break
        
        if top_matches:
            print(f"\nFound related notes for '{source_title}':")
            links_to_add = []
            
            # Read the current content of the source note to check for existing links
            with open(source_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            for match, score in top_matches:
                target_title = match["title"]
                
                # Check if the link already exists in the file to avoid duplicates
                if f"[[{target_title}]]" not in current_content:
                    links_to_add.append(f"[[{target_title}]]")
                    print(f"  - {target_title} (Similarity: {score:.2f})")
                    linked_count += 1
            
            # If we have new links to add, append them to the end of the note
            if links_to_add:
                new_content = current_content.strip() + "\n\n### Related Notes\n" + "\n".join(links_to_add)
                with open(source_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {os.path.basename(source_path)}")
                time.sleep(1) # Delay to not overwhelm the file system

    print(f"\nCompleted! Linked a total of {linked_count} notes.")
    print("Please check your vault for the new links under 'Related Notes' headings.")