import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_chroma import Chroma

load_dotenv()

# -------------------------
# Lazy loaders (IMPORTANT)
# -------------------------
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

@st.cache_resource
def load_vectorstore():
    embeddings = load_embeddings()
    return Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

def load_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    return ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        model="meta-llama/llama-3-8b-instruct",  # ⚡ faster & safer
        temperature=0,
        timeout=60
    )

# -------------------------
# Main RCA function
# -------------------------

def generate_rca(query: str):
    vectorstore = load_vectorstore()
    llm = load_llm()

    # Step 1: Retrieve similar incidents
    docs_with_scores = vectorstore.similarity_search_with_score(query, k=1)

    context = ""
    similarity_info = ""

    for doc, score in docs_with_scores:
        context += doc.page_content + "\n\n"
        similarity_info += f"Score: {score}\n{doc.page_content}\n\n"

    # Step 2: Prompt
    final_prompt = f"""
You are a Senior Production Support Engineer.

You MUST base your answer primarily on the retrieved incidents below.
Do NOT give generic answers.

Retrieved Historical Incidents:
{context}

New Incident:
{query}

If a similar incident exists:
- Mention the historical Incident ID
- Mention the Date
- Mention the exact Fix Applied

Then provide:
- Incident Summary (2 lines)
- Most Likely Root Cause
- Immediate Fix Steps (numbered)
- Long-Term Prevention
- Severity Level (P1 / P2 / P3)
- Confidence Score (0-100%)

Be precise and reference historical data.
"""

    # Step 3: LLM call
    response = llm.invoke(final_prompt)
    response_text = response.content

    # Step 4: Extract Severity
    severity = "Unknown"
    for level in ["P1", "P2", "P3"]:
        if level in response_text:
            severity = level
            break

    return response_text, similarity_info, severity
