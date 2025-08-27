import streamlit as st

from sql_handling import sql_chain_with_history
from query_router import router
from small_talk_handle import small_talk_chain_with_history
from pathlib import Path
from datetime import datetime
from typing import Optional

# Get API key securely from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"].strip()
GROQ_MODEL = "llama-3.3-70b-versatile"

# Initialize FAQ data
file_path = Path(__file__).parent / "resources/faq_data.csv"
ingest_faq_data(file_path)

st.title("E-Commerce Chatbot 🤖")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["session_id"] = "default_session"

# Welcome message
if not st.session_state["messages"]:
    with st.chat_message("assistant"):
        st.markdown("""
        👋 Welcome to our E-commerce Chatbot! I can help you with:
        - **Product queries** (e.g., 'Show me Nike shoes under ₹5000')
        - **FAQ questions** (e.g., 'What is your return policy?')
        - **General conversation** (e.g., 'Hello!')
        
        *Start by typing your question below!*
        """)

# Display chat history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Sidebar for session management
with st.sidebar:
    st.header("Chat Settings")
    
    # Session ID input
    session_id = st.text_input("Session ID", 
                              value=st.session_state["session_id"],
                              help="Unique ID for separate chat histories")
    
    if session_id != st.session_state["session_id"]:
        st.session_state["session_id"] = session_id
        st.session_state["messages"] = []
        st.rerun()
    
    # Clear chat history button
    if st.button("🧹 Clear Chat History"):
        clear_chat_history(st.session_state["session_id"])
        st.session_state["messages"] = []
        st.success("Chat history cleared!")
        st.rerun()
    
    # New session button
    if st.button("🆕 New Session"):
        new_id = f"session_{int(datetime.now().timestamp())}"
        st.session_state["session_id"] = new_id
        st.session_state["messages"] = []
        st.rerun()
    
    st.divider()
    
    # Session info
    st.write(f"**Current Session:** `{st.session_state['session_id']}`")
    st.write(f"**Messages:** {len(st.session_state['messages'])}")
    
    # Conversation statistics
    if st.session_state["messages"]:
        user_msgs = len([m for m in st.session_state["messages"] if m["role"] == "user"])
        assistant_msgs = len([m for m in st.session_state["messages"] if m["role"] == "assistant"])
        st.write(f"**User:** {user_msgs} | **Assistant:** {assistant_msgs}")

def ask(query):
    """Route query to appropriate handler."""
    try:
        route = router(query).name
        if route == "faq":
            return faq_chain_with_history(query, GROQ_API_KEY, GROQ_MODEL, session_id)
        elif route == "sql":
            return sql_chain_with_history(query, GROQ_API_KEY, GROQ_MODEL, session_id)
        elif route == "small_talk":
            return small_talk_chain_with_history(query, GROQ_API_KEY, GROQ_MODEL, session_id)
        else:
            return f"I'm not configured to handle '{route}' type queries yet."
    except Exception as e:
        st.error(f"Routing error: {str(e)}")
        return None

# Get user query
query = st.chat_input("Write your query...")

if query:
    # Display user message
    with st.chat_message(name="user"):
        st.markdown(query)
    st.session_state["messages"].append({"role": "user", "content": query})
    
    # Generate and display response with loading state
    with st.spinner("Thinking..."):
        try:
            response = ask(query)
            
            if response:
                with st.chat_message(name="assistant"):
                    st.markdown(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
            
        except Exception as e:
            error_msg = "Sorry, I encountered an error. Please try again."
            with st.chat_message(name="assistant"):
                st.markdown(error_msg)
            st.session_state["messages"].append({"role": "assistant", "content": error_msg})
            st.error(f"Error: {str(e)}")
    
    # Limit messages to prevent memory issues
    if len(st.session_state["messages"]) > 50:
        st.session_state["messages"] = st.session_state["messages"][-50:]
