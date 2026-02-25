import os
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector DB
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# LLM
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3-70b-instruct",
    temperature=0
)

def generate_rca(query):
    # Step 1: Retrieve similar documents
    docs_with_scores = vectorstore.similarity_search_with_score(query, k=3)
    
    context = ""
    similarity_info = ""

    for doc, score in docs_with_scores:
        context += doc.page_content + "\n\n"
        similarity_info += f"Score: {score}\n{doc.page_content}\n\n"

    # Step 2: Create Prompt manually
    final_prompt = f"""
You are a Senior Production Support Engineer.

You MUST base your answer primarily on the retrieved incidents below.
Do NOT give generic answers.

Based strictly on the retrieved historical incidents below:
{context}

New Incident:
{query}

If a similar incident exists:
- Mention the historical Incident ID
- Mention the Date it occurred
- Mention the exact Fix Applied previously

Then Provide:
- Incident Summary (2 lines)
- Most Likely Root Cause (be specific)
- Immediate Fix Steps (numbered)
- Long-Term Prevention
- Severity Level (P1/P2/P3)
- Confidence Score (0-100%)

Be precise and reference historical data explicitly. Avoid generic assumptions.
"""

     # Step 3: Call LLM
    response = llm.invoke(final_prompt)
    response_text = response.content

    # ✅ Extract Severity (Professional minimal way)
    severity = "Unknown"
    for level in ["P1", "P2", "P3"]:
        if level in response_text:
            severity = level
            break

    return response.content, similarity_info, severity