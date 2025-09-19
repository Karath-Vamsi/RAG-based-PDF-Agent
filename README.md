# InquisiDoc: A RAG-based PDF Agent

A research automation system built using **CrewAI**, **LangChain**, and **Large Language Models (LLMs)**. This project is designed to streamline the research process by utilizing Retrieval-Augmented Generation (RAG) techniques to ingest PDFs, gather insights from public and academic sources, and generate structured markdown reports with comparison tables on emerging technologies.

---

## 🧠 Features

- 🧾 **Automated PDF Ingestion**  
  Upload and process academic papers, whitepapers, or technical PDFs.

- 🔎 **RAG-based Information Retrieval**  
  Combine local document knowledge with live web search and academic APIs.

- 🧑‍🤝‍🧑 **Multi-Agent Collaboration**  
  Specialized agents (researcher, summarizer, comparator, reporter) coordinate tasks using CrewAI.

- 🧠 **LLM-Powered Analysis**  
  Agents use powerful language models to extract insights and summarize content.

- 📊 **Structured Output**  
  Generate markdown-based reports, technology comparisons, and decision matrices.

---

## 🏗️ Tech Stack

| Layer              | Tech Used                      |
|--------------------|--------------------------------|
| 🧠 LLM Backbone     | OpenAI GPT-4, Claude, or similar |
| 🕸 Retrieval Layer  | LangChain + Vector DB (e.g. FAISS, Chroma) |
| 🤖 Agent Framework | CrewAI                         |
| 📄 Data Sources     | Arxiv API, Semantic Scholar, Public Web, PDF files |
| 📑 Output Format    | Markdown (reports, tables)     |
