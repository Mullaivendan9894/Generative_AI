from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import os

from groq import Groq
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL")
parent_path = Path(__file__).parent if ("__file__") in locals() else Path.cwd()
faq_path = str(parent_path/ "resources/faq_data.csv")
ch_client = chromadb.Client()
collection_name = "faq"
groq_client = Groq()
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name = "all-MiniLM-L6-v2"
)


chat_sessions = {}

def add_chat_history(session_id, role, content):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    chat_sessions[session_id].append({
        "role": role,
        "content": content
    })

def get_chat_history(session_id, max_history = 6):
    return chat_sessions.get(session_id, [])[-max_history:]

def clear_chat_history(session_id):
    if session_id in chat_sessions:
        chat_sessions[session_id] = []

def ingest_faq_data(faq_path):
    if collection_name not in [col.name for col in ch_client.list_collections()]:
        collection = ch_client.get_or_create_collection(
        name = collection_name,
        embedding_function=ef
        )

        df = pd.read_csv(faq_path)

        docs = df["question"].to_list()
        metadatas = [{"answer": i} for i in df["answer"].to_list()]

        collection.add(
            documents = docs,
            metadatas = metadatas,
            ids = [f"id_{i+1}" for i in range(len(docs))]
        )
        print(f"FAQ Data successfully ingested into Chroma database. collection name: {collection_name}")
    else:
        print(f"Collection {collection_name} is already exist")

def get_relevant_answer(query):
    collection = ch_client.get_collection(name=collection_name)
    result = collection.query(
        query_texts = [query],
        n_results = 2
    )
    final_answer = " ".join([i.get("answer") for i in result["metadatas"][0]])
    return final_answer

def generate_answer_with_history(messages):
    result = groq_client.chat.completions.create(
    model= GROQ_MODEL,
    messages=messages,
    temperature=0.1,
    max_tokens=500
    )
    return result.choices[0].message.content

def faq_chain_with_history(query, session_id = "default"):
    context = get_relevant_answer(query)

    history = get_chat_history(session_id)

    messages = [
        {
            "role": "system",
            "content" : f'''You are a helpful FAQ assistant. Answer questions based on the provided context.
            If the answer isn't in the context, say "I don't know". Do not make things up.

            CONTEXT: {context}

            Important: Maintain conversational flow and consider the chat history when responding.'''
        }
    ]
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": query
    })

    answer = generate_answer_with_history(messages)
    

    add_chat_history(session_id, "user", query)
    add_chat_history(session_id, "assistant", answer)
    return answer

if __name__ == "__main__":
    ingest_faq_data(faq_path)
    answer = faq_chain_with_history("How do I use a promo code during checkout?")
    print(answer)
