[![GitHub repo](https://img.shields.io/badge/Conversational_RAG_Chatbot-blue?logo=github)](https://github.com/Mullaivendan9894/Generative_AI/tree/master/Conversational_RAG_Chatbot)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?logo=streamlit&logoColor=white)](https://conversational-rag-chatbot-v1.streamlit.app/)

# 🤖 Conversational RAG Chatbot

A Streamlit-based conversational chatbot that uses **Retrieval-Augmented Generation (RAG)** to answer questions about uploaded PDF documents. This project demonstrates how to build a document-based Q\&A system with chat history and source tracking.

-----

### 📋 Features

  * **PDF Document Processing:** Upload and process multiple PDF files.
  * **Conversational Interface:** Chat with your documents using a natural conversation style.
  * **Chat History:** Maintains conversation context across multiple queries.
  * **Source Tracking:** Shows which documents and pages were used to generate answers.
  * **Session Management:** Clear chat history while maintaining processed documents.

-----

### 🛠️ Technology Stack

  * **Streamlit:** Web application framework
  * **LangChain:** LLM application framework
  * **Groq API:** High-performance LLM inference (using Llama-3.3-70B)
  * **ChromaDB:** Vector database for document storage and retrieval
  * **HuggingFace Embeddings:** Sentence transformers for text embeddings
  * **PyPDF:** PDF document loading and processing

-----

### 📁 Project Structure

<pre>
rag-chatbot/
├── app.py                 # Streamlit web application
├── rag_chatbot.py         # Core RAG functionality
├── requirements.txt       # Python dependencies
├── st.secrets.toml       # API keys configuration
└── README.md             # This file
</pre>

-----

### ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd rag-chatbot
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up API keys:**
    Create a `st.secrets.toml` file with your Groq API key:
    ```toml
    GROQ_API_KEY = "your-groq-api-key-here"
    ```
    Install required packages:
    ```bash
    pip install streamlit langchain langchain-groq langchain-chroma langchain-community sentence-transformers pypdf
    ```

-----

### 🚀 Usage

1.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
2.  **Upload PDF files:**
      * Use the sidebar to upload one or more PDF documents.
      * Click "Process PDFs" to ingest the documents into the vector database.
3.  **Start chatting:**
      * Type questions in the chat input about your uploaded documents.
      * The chatbot will provide answers based on the document content.
      * View sources by expanding the "Sources" section under each response.
4.  **Manage conversations:**
      * Use "Clear Chat History" to start a new conversation while keeping processed documents.

-----

### 🔧 Configuration

  * **Environment Variables**
      * `GROQ_API_KEY`: Your Groq API key for LLM access
  * **Model Settings**
      * LLM Model: `llama-3.3-70b-versatile` (Groq)
      * Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`
      * Chunk Size: 1000 characters
      * Chunk Overlap: 200 characters
      * Retrieval Documents: 4 documents per query

-----

### 🧩 Core Functions

`rag_chatbot.py` Main Functions:

  * `initialize_components(GROQ_API_KEY)`: Sets up LLM and vector store
  * `ingest_documents(pdf_dir, GROQ_API_KEY)`: Processes and stores PDF documents
  * `query(question, GROQ_API_KEY, session_id)`: Gets answers with source tracking
  * `clear_session(session_id)`: Clears chat history for a session
  * `setup_rag_chain()`: Configures the RAG pipeline with conversation history

Key Components:

  * **Document Loading:** `PyPDFDirectoryLoader` for PDF processing
  * **Text Splitting:** `RecursiveCharacterTextSplitter` for chunking
  * **Vector Storage:** `ChromaDB` with `HuggingFace` embeddings
  * **Retrieval Chain:** History-aware retrieval with conversation context
  * **Session Management:** `ChatMessageHistory` for maintaining conversations

-----

### 📊 How It Works

  * **Document Processing:**
      * PDFs are loaded and split into manageable chunks.
      * Text chunks are converted to embeddings and stored in ChromaDB.
  * **Query Processing:**
      * User questions are processed with conversation context.
      * Relevant document chunks are retrieved from the vector store.
      * LLM generates answers based on retrieved context.
  * **Response Generation:**
      * Answers are generated using the provided document context.
      * Source documents and page numbers are tracked and displayed.
      * Conversation history is maintained for contextual understanding.

-----

### 🎯 Example Usage

```text
User: What are the main topics covered in these documents?
Assistant: Based on the documents, the main topics include...

[Sources]
- document1.pdf, Page number 3 / 45
- document2.pdf, Page number 1 / 32

User: Can you tell me more about topic X?
Assistant: Certainly! Topic X is discussed in detail...
```
