__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import os
import tempfile
import streamlit as st
from build_agent import build_pdf_agent
from logs import log_conversation_to_file, LOG_FILE_PATH, LOG_DIR

def main():
    st.set_page_config(page_title="InquisiDoc: A RAG-based PDF Agent", layout="wide")
    
    # Custom CSS for a better look
    st.markdown("""
    <style>
    .reportview-container {
        flex-direction: column;
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stButton>button {
        color: #fff;
        background-color: #4CAF50;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📄 InquisiDoc: A RAG-based PDF Agent")
    
    # Sidebar for project abstract and features
    with st.sidebar:
        st.header("Project Overview")
        st.markdown("""
        **InquisiDoc** is a RAG-based PDF Agent system built with CrewAI and LangChain. 
        It automates the research process by ingesting PDFs, and using multi-agent collaboration to extract insights and generate structured reports.
        """)
        st.markdown("---")
        st.subheader("Key Features 🧠")
        st.markdown("""
        - **Automated PDF Ingestion**: Upload and process academic papers or whitepapers.
        - **RAG-based Retrieval**: Combine PDF knowledge with external sources.
        - **Multi-Agent Collaboration**: Specialized agents work together to analyze content.
        - **Structured Output**: Generate reports with key insights and comparisons.
        """)

    # Main content area
    uploaded_file = st.file_uploader("Upload a PDF to get started", type=["pdf"])

    # Initializing session state
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = None
    if "log_initialized" not in st.session_state:
        st.session_state.log_initialized = False
    if "pdf_loaded" not in st.session_state:
        st.session_state.pdf_loaded = False
    if "uploaded_pdf_name" not in st.session_state:
        st.session_state.uploaded_pdf_name = None
    if "log_file_path" not in st.session_state:
        st.session_state.log_file_path = LOG_FILE_PATH
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Handle file upload and agent initialization
    if uploaded_file:
        if uploaded_file.name != st.session_state.uploaded_pdf_name:
            # Rotate log file for previous PDF
            if st.session_state.log_initialized and os.path.exists(st.session_state.log_file_path):
                rotated_name = f"log_{st.session_state.uploaded_pdf_name}.txt".replace(" ", "_")
                rotated_path = os.path.join(LOG_DIR, rotated_name)
                os.rename(st.session_state.log_file_path, rotated_path)

            st.session_state.agent_executor = None
            st.session_state.log_initialized = False
            st.session_state.pdf_loaded = False
            st.session_state.uploaded_pdf_name = uploaded_file.name
            log_filename = f"log_{uploaded_file.name}.txt".replace(" ", "_")
            st.session_state.log_file_path = os.path.join(LOG_DIR, log_filename)

        if not st.session_state.pdf_loaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_pdf_path = tmp_file.name

            st.success("PDF uploaded! Initializing agent...")
            with st.spinner("Processing PDF and building agent..."):
                st.session_state.agent_executor = build_pdf_agent(tmp_pdf_path)
                st.session_state.pdf_loaded = True

            if not os.path.exists(st.session_state.log_file_path):
                open(st.session_state.log_file_path, "w").close()
            st.session_state.log_initialized = True
            
            # Clear messages for new PDF
            st.session_state.messages = []

    # Display chat messages from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input and agent interaction
    if st.session_state.agent_executor:
        user_question = st.chat_input("Ask a question about the PDF")
        if user_question:
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.agent_executor.invoke({"input": user_question})
                    st.markdown(response["output"])
                    st.session_state.messages.append({"role": "assistant", "content": response["output"]})
                    
            # Log conversation
            log_conversation_to_file(st.session_state.agent_executor.memory.chat_memory.messages, st.session_state.log_file_path)

        # Download conversation log button
        if os.path.exists(st.session_state.log_file_path):
            with open(st.session_state.log_file_path, "r") as f:
                st.download_button(
                    "Download Conversation Log",
                    f,
                    file_name=os.path.basename(st.session_state.log_file_path)
                )

if __name__ == "__main__":
    main()