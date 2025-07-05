# ingest.py (updated for PDF support)
import os
import time
import shutil
import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# --- CHANGE 1: Import the necessary PDF loader ---
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader

# Conditional imports for embedding models remain the same
if settings.MODEL_PROVIDER == "google":
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
elif settings.MODEL_PROVIDER == "local":
    from langchain_huggingface import HuggingFaceEmbeddings
else:
    raise ValueError(f"Invalid MODEL_PROVIDER: {settings.MODEL_PROVIDER}. Choose 'google' or 'local'.")


def get_embedding_model():
    """Initializes and returns the appropriate embedding model based on settings."""
    if settings.MODEL_PROVIDER == "google":
        print("Using Google Gemini for embeddings.")
        if not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
        return GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL)
    elif settings.MODEL_PROVIDER == "local":
        print(f"Using local HuggingFace model for embeddings: {settings.LOCAL_EMBEDDING_MODEL}")
        model_kwargs = {'device': 'cpu', 'trust_remote_code': True}
        encode_kwargs = {'normalize_embeddings': False}
        return HuggingFaceEmbeddings(
            model_name=settings.LOCAL_EMBEDDING_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )


def create_vector_store():
    """Loads documents, splits them, creates embeddings, and saves them to a FAISS index."""
    docs_path = "./docs"
    faiss_index_path = "faiss_index"

    if os.path.exists(faiss_index_path):
        print(f"Deleting existing index at '{faiss_index_path}'...")
        shutil.rmtree(faiss_index_path)

    # --- CHANGE 2: Load each file type with its specific loader ---
    print(f"📁 Loading documents from '{docs_path}'...")

    # Load Markdown files
    md_loader = DirectoryLoader(
        docs_path, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}
    )
    md_documents = md_loader.load()
    print(f"✅ Loaded {len(md_documents)} Markdown documents.")

    # Load PDF files
    pdf_loader = DirectoryLoader(docs_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    pdf_documents = pdf_loader.load()
    print(f"✅ Loaded {len(pdf_documents)} PDF documents.")

    # Combine all loaded documents
    all_documents = md_documents + pdf_documents
    # --- END OF CHANGES ---

    if not all_documents:
        print("⚠️ No documents were found. Exiting.")
        return

    print(f"✅ Total documents loaded: {len(all_documents)}.")
    print("✂️ Splitting documents into chunks...")
    # Use the combined list for splitting
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(all_documents)
    print(f"✅ Split into {len(chunks)} chunks.")

    print("🧠 Creating embeddings and building FAISS index...")
    try:
        embeddings = get_embedding_model()
        start_time = time.time()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        end_time = time.time()
        print(f"✅ FAISS index built in {end_time - start_time:.2f} seconds.")

        print(f"💾 Saving FAISS index to '{faiss_index_path}'...")
        vectorstore.save_local(faiss_index_path)
        print(f"✅ FAISS index saved successfully using '{settings.MODEL_PROVIDER}' provider.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return

if __name__ == "__main__":
    create_vector_store()