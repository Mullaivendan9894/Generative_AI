import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain_groq import ChatGroq 
from langchain_huggingface.embeddings import HuggingFaceEmbeddings 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import FAISS 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain.chains import create_history_aware_retriever 
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.chains import create_retrieval_chain 
from langchain_community.chat_message_histories import ChatMessageHistory 
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")



### Setup Streamlit app
st.title("Converstional RAG with pdf uploads and chat history")
st.write ("Upload pdf's and chat with their content")


## Iput the Groq API key
api_key = st.text_input("Enter your Groq API key: ", type = "password")

## Check if groq api key is provided
if api_key:
    llm = ChatGroq(model = "Llama-3.3-70b-Specdec", groq_api_key = api_key)

    ## Chat interface
    session_id = st.text_input("Session ID", value = "default_Session")

    ## Statefully magange the chat history

    if "store" not in st.session_state:
        st.session_state.store = {}
    
    uploaded_files = st.file_uploader("Chosse a PDF file", type = "pdf", accept_multiple_files = True)

    ## Process uploaded PDF's

    if uploaded_files:
        documents = []

        for uploaded_files in uploaded_files:
            temp_pdf = f"./temp.pdf"
            with open(temp_pdf, "wb") as file:
                file.write(uploaded_files.getvalue())
                file_name = uploaded_files.name

            loader = PyPDFLoader(temp_pdf)
            docs = loader.load()
            documents.extend(docs)

        ## Splitting and creating the embeddings for the documents

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 10000, chunk_overlap = 1000)
        splits = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(documents = splits, embedding = embeddings)
        retriever = vector_store.as_retriever()


        ## Create the Prompts
        contextualize_question_system_prompt = (
        "Based on the chat history and the most recent user question, "
        "which may refer to previous context in the conversation, "
        "reformulate the question so it can be understood independently of the chat history. "
        "Do not provide an answer; simply rephrase the question if necessary, otherwise return it unchanged."
        )

        contextualize_question_prompt = ChatPromptTemplate.from_messages(
        [ 
                ("system", contextualize_question_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ]
        )


        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_question_prompt)


       ## System prompt
        system_prompt = (
            "You are a highly knowledgeable assistant tasked with providing accurate answers to questions."
            "Utilize the given pieces of retrieved information to craft your response."
            "If the answer is not present in the provided context, indicate that you do not know."
            "Your responses should be detailed and comprehensive."
            "\n\n"
            "{context}"
        )

        question_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, question_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)



        def get_session_history(session: str) -> BaseChatMessageHistory:
            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
            return st.session_state.store[session_id]
        

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key = "input",
            history_messages_key = "chat_history",
            output_messages_key = "answer"
        )

        
        user_input = st.text_input("Your question: ")

        if user_input:
            session_history = get_session_history(session_id)
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config = {
                    "configurable": {"session_id": session_id}
                },
            )

            st.write(st.session_state.store)
            st.success(f'''Assistant: {response["answer"]}''')
            st.write(f'''Chat History: {session_history.messages}''')
else:
    st.warning("Please enter the Groq API key")

