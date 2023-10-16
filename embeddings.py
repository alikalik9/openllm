import json
import os
from datetime import datetime
from typing import List, Dict
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.memory.chat_memory import ChatMessageHistory
from nicegui import Client, ui
from main import ChatApp

class Embedding(ChatApp):
    def __init__(self):
        super().__init__()  # Call the initializer of the parent class
        # Add any additional initialization code here

    # Add any additional methods here
    def print(self):
        print(self.api_key)
