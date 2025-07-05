# app.py (updated)
import os
import streamlit as st
import settings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.vectorstores import FAISS

# --- Conditional Imports and Model Initialization ---

if settings.MODEL_PROVIDER == "google":
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    # Configure Google API key
    if 'google_api_key' not in st.session_state:
        st.session_state.google_api_key = st.secrets.get("GOOGLE_API_KEY", settings.GEMINI_API_KEY)
    os.environ["GOOGLE_API_KEY"] = st.session_state.google_api_key

elif settings.MODEL_PROVIDER == "local":
    from langchain_community.chat_models.ollama import ChatOllama
    from langchain_huggingface import HuggingFaceEmbeddings

else:
    st.error(f"Invalid MODEL_PROVIDER in settings.py: {settings.MODEL_PROVIDER}")
    st.stop()


# --- UI SETUP ---
st.set_page_config(page_title=f"{settings.MODEL_PROVIDER.capitalize()} RAG Chatbot", page_icon="📚")
st.title(f"🔍 {settings.MODEL_PROVIDER.capitalize()} RAG Bot")
st.write("Ask this chatbot anything about the documents in the `./docs` folder.")


# --- KNOWLEDGE BASE LOADING ---
@st.cache_resource(show_spinner="🗂️ Loading knowledge base...")
def load_knowledge_base():
    """Loads the FAISS index and initializes the correct embedding model."""
    faiss_index_path = "faiss_index"
    if not os.path.exists(faiss_index_path):
        st.error(f"FAISS index not found. Please run the `ingest.py` script first with MODEL_PROVIDER='{settings.MODEL_PROVIDER}'.")
        st.stop()

    # Load the appropriate embedding model
    if settings.MODEL_PROVIDER == "google":
        embeddings = GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL)
    else: # local
        # --- THE FIX IS HERE ---
        # We must add trust_remote_code=True, just like in the ingest script.
        model_kwargs = {'device': 'cpu', 'trust_remote_code': True}
        encode_kwargs = {'normalize_embeddings': False}
        # embeddings = HuggingFaceEmbeddings(
        #     model_name=settings.LOCAL_EMBEDDING_MODEL,
        #     model_kwargs=model_kwargs,
        #     encode_kwargs=encode_kwargs
        # )
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.LOCAL_EMBEDDING_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore.as_retriever(search_kwargs={"k": 5})

# --- LLM and CHAIN INITIALIZATION ---
@st.cache_resource(show_spinner="🤖 Initializing models...")
def initialize_chain():
    """Initializes the LLM, memory, and RAG chain."""
    retriever = load_knowledge_base()

    # Initialize the appropriate LLM
    if settings.MODEL_PROVIDER == "google":
        llm = ChatGoogleGenerativeAI(model=settings.GEMINI_CHAT_MODEL, temperature=0.5, convert_system_message_to_human=True)
    else: # local
        llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.LOCAL_LLM_MODEL, temperature=0.3)

    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True, output_key="answer")

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False,
    )

# --- Main App Logic ---
qa_chain = initialize_chain()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        try:
            result = qa_chain.invoke({"question": user_input})
            response = result["answer"]
        except Exception as e:
            response = f"Sorry, an error occurred: {e}"

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})