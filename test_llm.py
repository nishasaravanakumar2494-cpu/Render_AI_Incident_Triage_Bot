import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3-70b-instruct",
    temperature=0
)

response = llm.invoke("Say hello")
print(response.content)