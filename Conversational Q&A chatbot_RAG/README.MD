# Conversational RAG with PDF Uploads and Chat History

This project demonstrates a **Conversational Retrieval-Augmented Generation (RAG)** system that allows users to upload PDF files, extract content, and interact with it using a conversational interface. The system maintains chat history and provides accurate responses based on the uploaded documents. The project uses **LangChain**, **Streamlit**, and **FAISS** for implementation.

---

## Features

- **PDF Upload**: Users can upload multiple PDF files.
- **Text Splitting and Embedding**: Uploaded PDF content is processed, split into chunks, and embedded using HuggingFace sentence-transformers.
- **Conversational Interface**: A chat-based interface powered by the Groq LLM for interacting with the uploaded document content.
- **Chat History**: Maintains chat session history for seamless interactions.
- **Retrieval-Augmented Generation (RAG)**: Combines information retrieval and generative response capabilities.

---

## Tech Stack

- **Python**: Programming language.
- **Streamlit**: For building the web interface.
- **LangChain**: For handling RAG pipelines.
- **FAISS**: For vector storage and similarity search.
- **HuggingFace Embeddings**: For text embedding.
- **Groq LLM**: For generating responses.

