from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
import re


def tavily_tool():
    return TavilySearchResults(k=3)

@tool
def extract_key_points(text: str) -> str:
    """Extracts key takeaways or bullet points from a section of the document."""
    return (
        "Please extract the most important key points or action items from the following text:\n\n"
        f"{text}"
    )

@tool
def generate_questions(text: str) -> str:
    """Generates thoughtful questions based on the given document content."""
    return (
        "Based on the following content, generate 5 insightful questions that someone might ask:\n\n"
        f"{text}"
    )

@tool
def extract_timeline(text: str) -> str:
    """Extracts the flow or structure (sections, chapters, or chronology) from the content."""
    return (
        "Analyze the following content and provide a high-level outline or timeline of the sections covered:\n\n"
        f"{text}"
    )

@tool
def extract_citations(text: str) -> str:
    """Lists all citations, references, or bibliography entries from the content."""
    return (
        "Identify and list all citation or reference entries from the following content:\n\n"
        f"{text}"
    )


@tool
def auto_highlight_keywords(text: str) -> str:
    """Automatically highlights important keywords in the given text."""
    prompt = f"Extract the most important keywords from the following text, comma separated:\n\n{text}"
    llm = ChatOpenAI(model="mistralai/mistral-7b-instruct", temperature=0)
    keywords_response = llm.predict(prompt)
    
    # Clean keywords list
    keywords = [kw.strip() for kw in keywords_response.split(",") if kw.strip()]
    
    # Highlighting those keywords in text
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub(lambda m: f"**{m.group(0)}**", text)
    return text
