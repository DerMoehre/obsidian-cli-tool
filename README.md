## Obsidian Semantic Note Assistant CLI
### Overview
This project is a powerful command-line interface (CLI) tool designed to enhance your Obsidian note-taking workflow. By leveraging a local Ollama server, the tool can analyze your Markdown notes to find semantically similar content and provide actionable feedback on note quality. This automates two key processes of a "second brain" system: creating connections between ideas and refining the quality of individual notes.

### Key Features
- Semantic Linking (--note-linker): This feature scans your entire vault, calculates vector embeddings for each note, and identifies the most semantically similar notes. It then automatically adds links to these related notes under a "Related Notes" heading, helping you build a more robust knowledge graph.

- Note Quality Rating (--note-quality): This function sends the content of each note to a general-purpose language model to get a rating and constructive feedback. It rates the density and completeness of the information on a scale of 1-10 and appends the results to a new "Note Quality" section within the note itself.

- The Note-Quality is set as a note property, so that it can be visualized with the new `Obsidian Bases` module

### SetUp
- Change the `.env.temp` file to `.env`
- Set your vault directory in the `.env`
    - Example for Windows: `C:\\Users\\YourUser\\Documents\\ObsidianVault`
    - Example for macOS/Linux: `/Users/YourUser/Documents/ObsidianVault`

### How to Use
The tool is executed from the command line, where you choose which action to perform and provide the path to your Obsidian vault.

- To create semantic links between notes:
```Bash
python main.py --note-linker
```

- To rate the quality of your notes:
```Bash
python main.py --note-quality
```

### Requirements
- Python 3.x: The script is written in Python.
- Ollama: The tool requires a local Ollama server running in the background.
- Ollama Models: You must have the necessary models pulled. `nomic-embed-text` for embeddings and `llama3` for rating recommended
- Use a virtual environment to install the dependencies
```Bash
python -m venv .venv
```
Then, install the dependencies using the following command:
```Bash
uv pip install -e .
```

