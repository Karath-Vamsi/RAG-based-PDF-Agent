from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.tools import tool
from my_tools import tavily_tool, extract_key_points, generate_questions, extract_timeline, extract_citations, auto_highlight_keywords
import os

load_dotenv()

system_instructions = """
You are a helpful assistant that answers questions about an uploaded PDF. You have access to several tools.

Only use tools when needed, and always choose the single most appropriate tool based on the user's question. If no tool is needed, respond directly and concisely.

Your available tools:
- retrieve_pdf_context: Get relevant excerpts from the PDF for a user’s question.
- extract_key_points: Summarize key bullet points from a section of text.
- generate_questions: Create thoughtful questions from the content.
- extract_timeline: Provide a timeline or high-level structure of the document.
- extract_citations: List all references or citations in the document.
- tavily_search: Use for questions that cannot be answered from the PDF.
- auto_highlight_keywords: Enhance any output by bolding important terms.

Usage instructions:
- For questions about the PDF's content, first use `retrieve_pdf_context`.
- If the user asks for summaries, key points, or takeaways, use `extract_key_points`.
- For structure or flow, use `extract_timeline`.
- If asked about citations or references, use `extract_citations`.
- For general questions unrelated to the PDF, use `tavily_search`.
- After any tool returns a result (except `tavily_search`), apply `auto_highlight_keywords` to that result.

Only use `auto_highlight_keywords` after another tool has returned a full answer.

You must always respond by calling tools in the correct sequence (e.g. one tool, then keyword highlighting if applicable). Do not return multiple tool calls at once. Do not guess — always call tools when the answer is not directly known.
"""



def setup_tools():
    return [tavily_tool(),
            extract_key_points,
            generate_questions,
            extract_timeline,
            extract_citations,
            auto_highlight_keywords]

def pdf_build_and_split(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents(pages)

    # Embed + store
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vectordb = Chroma.from_documents(docs, embedding=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    return retriever

def build_pdf_agent(pdf_path: str):
    retriever = pdf_build_and_split(pdf_path)

    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="openai/gpt-4.1-nano", # this is not free, make limited calls per day
        temperature=0.5,
        max_tokens=750
    )

    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instructions),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    @tool
    def retrieve_pdf_context(query: str) -> str:
        """Answer questions by retrieving relevant content from the uploaded PDF."""
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return "No relevant content found in the PDF."
        return "\n\n".join(doc.page_content for doc in docs)


    # tool setup
    all_tools = setup_tools() + [retrieve_pdf_context]

    # Agent w/ memory
    agent = create_tool_calling_agent(llm, all_tools, prompt)
    executor = AgentExecutor(agent=agent, tools=all_tools, memory=memory, verbose=True)

    return executor
