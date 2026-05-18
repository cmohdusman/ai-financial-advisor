from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, MODEL

from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationChain

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=MODEL,
    temperature=0.3
)
