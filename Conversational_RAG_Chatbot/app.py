import streamlit as st
import tempfile
from pathlib import Path
from rag_chatbot import ingest_documents, query, clear_session

# Set page config
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents_ingested" not in st.session_state:
    st.session_state.documents_ingested = False

# Get API key from secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"].strip()
except:
    st.error("Please set GROQ_API_KEY in Streamlit secrets")
    st.stop()

st.title("🤖 Converstional RAG with pdf uploads and chat history")
st.write("Upload PDFs and ask questions about their content")

with st.sidebar:
# PDF Upload Section
    st.header("📁 Upload PDFs")
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type="pdf", 
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process PDFs"):
        with st.spinner("Processing PDFs..."):
            # Create temporary directory for uploaded PDFs
            temp_dir = tempfile.mkdtemp()
            for uploaded_file in uploaded_files:
                file_path = Path(temp_dir) / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            try:
                num_chunks = ingest_documents(temp_dir, GROQ_API_KEY)
                st.session_state.documents_ingested = True
                st.success(f"Processed {len(uploaded_files)} PDF(s)! Ready to chat.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.divider()
    # Clear chat button
    if st.button("Clear Chat History"):
        clear_session("default")
        st.session_state.messages = []
        st.rerun()


if not st.session_state.documents_ingested:
    st.info("Please upload and process PDFs first")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.write(f"{source}")

    # Chat input
    prompt = st.chat_input("Ask a question about your PDFs...")
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer, sources = query(prompt, GROQ_API_KEY)
                    st.markdown(answer)
                    
                    # Show sources if available
                    if sources:
                        with st.expander("📚 Sources:"):
                            for source in sources:
                                st.write(f"{source}")
                        
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")

 