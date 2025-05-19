import os
from dotenv import load_dotenv
from pandasai.llm import OpenAI as PandasOpenAI
from openai import OpenAI
from langchain_openai import ChatOpenAI

load_dotenv()

pandas_llm = PandasOpenAI(
    api_token=os.getenv("OPENAI_API_KEY"),
)

agent_llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))