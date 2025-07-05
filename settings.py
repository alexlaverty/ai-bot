# settings.py
import os
MODEL_PROVIDER = "local"  # Options: "google", "local"

# --- Google Gemini Configuration ---
# (Only used if MODEL_PROVIDER is "google")
# GEMINI_API_KEY = "" # It's better to load this from st.secrets or .env
# GEMINI_EMBEDDING_MODEL = "models/embedding-001"
# GEMINI_CHAT_MODEL = "gemini-1.5-flash"

# --- Local Ollama Configuration ---
# (Only used if MODEL_PROVIDER is "local")
# Make sure Ollama is running and you have pulled the models you want to use.
# In your terminal, run:
# ollama pull llama3
# ollama pull nomic-embed-text

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Model for generating text (chat)
LOCAL_LLM_MODEL = "llama3:8b"

# Model for creating embeddings (for RAG)
# nomic-embed-text is a strong open-source embedding model.
LOCAL_EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"