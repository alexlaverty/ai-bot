# AI Chat Bot

This repository provides a **local, privacy-first AI chatbot** that can answer questions about your personal knowledge base using Retrieval-Augmented Generation (RAG). The bot leverages your own Markdown documents, builds a vector database for semantic search, and uses a local LLM (via [Ollama](https://ollama.com/)) for chat. Everything runs locally in Docker containers for maximum security and flexibility.

---

## Features

- **Private, local-first RAG chatbot** (no cloud required)
- **Custom knowledge base**: Add your own Markdown files to the `docs/` folder
- **Semantic search**: Finds relevant info from your docs using embeddings
- **Supports local LLMs** via Ollama (e.g., Llama 3)
- **Easy setup** with Docker Compose
- **Streamlit web UI** for chatting

---

## How It Works

1. **Knowledge Base Generation**:
   Your Markdown files in `docs/` are processed and converted into vector embeddings. This enables the chatbot to semantically search your documents for relevant information.

2. **Retrieval-Augmented Generation (RAG)**:
   When you ask a question, the bot retrieves the most relevant document chunks and feeds them to the LLM, so answers are grounded in your actual data.

3. **Local LLM via Ollama**:
   All AI inference runs on your machine. You control the models and your data never leaves your computer.

---

## Getting Started

### 1. Prepare Your Knowledge Base

- Place your custom Markdown files in the [`docs/`](docs/) folder.
- Each file can contain any information you want the bot to know (examples: notes, manuals, personal data, etc.).

### 2. Configure the Model

- Edit [`chatbot/settings.py`](chatbot/settings.py) and set:
  - `MODEL_PROVIDER = "local"`
  - `LOCAL_LLM_MODEL` to the model you want (e.g., `"llama3:8b"`)
- Make sure [Ollama](https://ollama.com/) is installed and running:
  ```sh
  ollama serve
  ```
- Pull the required models:
  ```sh
  ollama pull llama3
  ollama pull nomic-embed-text
  ```

### 3. Generate the Vector Knowledge Base

- This step processes your Markdown files and builds the FAISS vector index for semantic search.
  ```sh
  python ingest.py
  ```
- After running, you should see a new [`faiss_index/`](faiss_index/) folder.

### 4. Start the Chatbot (Docker Compose)

- From the project root, run either :

  ```
  pip install -r requirements.txt
  streamlit run chatbot.py
  ```

  or via docker :

  ```sh
  docker compose up --build
  ```
- This will build and start the chatbot container.

### 5. Chat With Your Bot

- Open your browser and go to: [http://localhost:8501](http://localhost:8501)
- Ask questions about your documents!

---

## Tips

- **Add or update docs**: Place new Markdown files in `docs/` and re-run `python ingest.py` to update the knowledge base.
- **Model selection**: You can experiment with different local models by changing the settings and pulling them with Ollama.
- **Privacy**: All data and models run locally. Nothing is sent to the cloud.

---

## What is RAG and Why Markdown?

- **RAG (Retrieval-Augmented Generation)** combines search and generation: it finds relevant info from your docs and uses it to answer questions, making the bot more accurate and grounded.
- **Markdown** is used for your knowledge base because it's easy to write, organize, and version control.

---

## Example Workflow

1. Write your notes in Markdown and save them in `docs/`.
2. Run `python ingest.py` to build the vector index.
3. Start Ollama and pull your desired models.
4. Launch the chatbot with Docker Compose.
5. Chat with your AI assistant about anything in your docs!

---

## Troubleshooting

- If you see errors about missing FAISS index, make sure you ran `python ingest.py` after adding docs.
- If the chatbot can't start, check that Ollama is running and the model names in `settings.py` match what you have pulled.

---

Enjoy your private, local AI assistant.