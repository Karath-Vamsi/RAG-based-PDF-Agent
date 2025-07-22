import os
import tempfile
import streamlit as st
from build_agent import build_pdf_agent
from logs import log_conversation_to_file, LOG_FILE_PATH, LOG_DIR

def main():
    st.set_page_config(page_title="RAG Agent PDF Chat", layout="centered")
    st.title("Ask Questions About Your PDF")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

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

    if uploaded_file:
        if uploaded_file.name != st.session_state.uploaded_pdf_name:
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
            st.session_state.agent_executor = build_pdf_agent(tmp_pdf_path)
            st.session_state.pdf_loaded = True

            # To ensure the log file exists (new or resumed session)
            if not os.path.exists(st.session_state.log_file_path):
                open(st.session_state.log_file_path, "w").close()
            st.session_state.log_initialized = True

    if st.session_state.agent_executor:
        user_question = st.text_input("Ask a question about the PDF")
        if user_question:
            with st.spinner("Thinking..."):
                response = st.session_state.agent_executor.invoke({"input": user_question})
                log_conversation_to_file(
                    st.session_state.agent_executor.memory.chat_memory.messages,
                    st.session_state.log_file_path
                )

            st.markdown("### Answer")
            st.write(response["output"])

        # Downloading conversation log
        if os.path.exists(st.session_state.log_file_path):
            with open(st.session_state.log_file_path, "r") as f:
                st.download_button(
                    "Download Conversation Log",
                    f,
                    file_name=os.path.basename(st.session_state.log_file_path)
                )

if __name__ == "__main__":
    main()
