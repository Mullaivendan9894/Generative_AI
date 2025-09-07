import streamlit as st
from uuid import uuid4
from pathlib import Path
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


chunk_size = 1000
chunk_overlap = 200
collection_name = "QandA"
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
base_path = Path(__file__).parent if "__file__" in locals() else Path.cwd()
pdf_dir = str(base_path/ "standards")
vectorstore_dir = str(base_path/"resources/vectorstore")

GROQ_MODEL = "llama-3.3-70b-versatile"

llm = None
vector_store = None
session_store = {}

def initialize_components(GROQ_API_KEY):
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(model = GROQ_MODEL, api_key = GROQ_API_KEY)
    
    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name = embedding_model,
            model_kwargs  = {"trust_remote_code": True}
        )

        vector_store = Chroma(
            collection_name = collection_name,
            embedding_function = ef,
            persist_directory = vectorstore_dir

        )

def get_session_history(session_id) -> ChatMessageHistory:
    '''Get or create a session history for a session'''
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


def setup_rag_chain():
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", """Rephrase the latest question to be standalone based on the chat history. 
            If the question is already clear or history is insufficient, return it unchanged. 
            Do not answer the question or add assumptions."""),
        MessagesPlaceholder("chat_history"),
        ("human","{input}")
    ])

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a precise assistant. Answer the question using only the provided documents: {context}. 
            For questions requesting lists, provide up to 5 items in a numbered list. 
            For other questions, give a comprehensive answer. If documents don’t fully answer the question, say 'I don’t have enough information to fully answer. 
            If no relevant documents are found, say 'No relevant information found.' Do not fabricate details."""),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})  # Limited to 4 documents
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )
    document_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )


def ingest_documents(pdf_dir, GROQ_API_KEY):
    """
    Process and store documents from URLs.
    
    Args:
        urls: List of URLs to load and process
    """
    global vector_store

    initialize_components(GROQ_API_KEY)
    vector_store.reset_collection()

    loader = PyPDFDirectoryLoader(pdf_dir)
    documents = loader.load()


    text_splitter = RecursiveCharacterTextSplitter(
        separators = ["\n\n", "\n", ".", " "],
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )

    chunks = text_splitter.split_documents(documents)

    uuids = [str(uuid4()) for _ in chunks]

    vector_store.add_documents(
        documents = chunks,
        ids = uuids
    )

def query(question, GROQ_API_KEY, session_id = "default"):
    """
    Get an answer to a question with sources.
    
    Args:
        question: The query to process
        session_id: Conversation session identifier
        
    Returns:
        Tuple of (answer, list_of_source_urls)
    """
    initialize_components(GROQ_API_KEY)
    rag_chain = setup_rag_chain()

    result = rag_chain.invoke(
        {"input": question},
        config={"configurable": {"session_id": session_id}}
    
    )

    sources = [doc.metadata["source"] for doc in result["context"] if "source" in doc.metadata]
    sources = []
    for i in result["context"]:
        sources.append(f'''{i.metadata["source"]}, Page number {i.metadata["page_label"]} / {i.metadata["total_pages"]}''')

    return result["answer"], sources

def clear_session(session_id: str):
    """Clear chat history for a specific session."""
    if session_id in session_store:
        del session_store[session_id]


if __name__ == "__main__":
    ingest_documents(pdf_dir)

    answer , sources = query("Who is Dhaval Patel and his experience?")
    print(answer)
    print("--------------------")
    print(sources)
