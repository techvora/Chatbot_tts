import os
from typing import List, Dict
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


class ChatManager:
    def __init__(self, model: str = "gemini-1.5-pro"):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.conversation_history: List[Dict] = []

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def chat_function(self, user_prompt: str) -> str:
        self.add_to_history("user", user_prompt)

        llm = ChatGoogleGenerativeAI(model=self.model, api_key=self.google_api_key)

        prompt = PromptTemplate(
            template="You are a Multi talented chatbot named BOT Buddy.\n\n You are capable to answer any type of question and you are good in chat conversation so give answer for below query/chat \n\nQuestion: {query}",
            input_variables=["query"]
        )

        result = (prompt | llm).invoke({"query": user_prompt})
        self.add_to_history("assistant", result.content)
        return result.content

    def clear_history(self):
        self.conversation_history = []
