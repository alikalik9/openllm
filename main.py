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

API_KEY = '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'

class ChatApp:
    def __init__(self):
        self.llm = ConversationChain(llm=ChatOpenAI(model_name="mistral-7b-instruct", openai_api_key='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', openai_api_base="https://api.perplexity.ai"), memory=ConversationBufferMemory())
        self.messages = []
        self.thinking = False
        self.total_tokens = 0
        self.chatloaded = False
        self.current_chat_name = ""

    def on_value_change(self, ename="mistral-7b-instruct", etemp="1"):
        self.llm = ConversationChain(llm=ChatOpenAI(model_name=ename, temperature=etemp, openai_api_key='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', openai_api_base="https://api.perplexity.ai"))

    @ui.refreshable
    async def chat_messages(self) -> None:
        for name, text in self.messages:
            ui.chat_message(text=text, name=name, sent=name == 'You').props(f"bg-color={('teal' if name == 'You' else 'primary')} text-color=white").classes("rounded-lg text-lg")
        if self.thinking:
            ui.spinner("dots",size='3rem')
        await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', respond=False)
    
    @ui.refreshable
    def chat_history_grid(self): #function for the table with the chat history
        current_directory = os.getcwd()
        json_directory = os.path.join(current_directory, 'chat_history')   
        json_filenames = [f for f in os.listdir(json_directory) if f.endswith('.json')] #list all json files in directory
        rowData = [{'filename': filename} for filename in json_filenames]
        grid = ui.aggrid({
    'defaultColDef': {'flex': 1},
    'columnDefs': [
        {'headerName': 'Chats', 'field': 'filename'},
    ],
    'rowData': rowData,
    'rowSelection': 'multiple',
}, theme="material").classes('md:h-1/2 max-h-200 pt-4').on("cellClicked", lambda event:  self.load_chat_history(event.args["value"]))


    async def send(self, text) -> None:
        message = text.value
        self.messages.append(('You', text.value))
        self.thinking = True
        text.value = ''
        self.chat_messages.refresh()
        with get_openai_callback() as cb:
            response = await self.llm.arun(message)
        self.tokens_used = cb.total_tokens  # get the total tokens used
        print(self.tokens_used)
        self.messages.append(('GPT', response))
        await self.save_to_db(self.messages_to_dict(self.llm.memory.chat_memory.messages))# Save the chat history to the database
        self.chat_history_grid.refresh()
        self.thinking = False
        self.chat_messages.refresh()

    async def clear(self):
        self.llm.memory.clear()
        self.messages.clear()
        self.current_chat_name=""
        self.chat_messages.refresh()
        


    def messages_to_dict(self, messages: List) -> List[Dict]:
        return [{'type': type(m).__name__, 'content': m.content} for m in messages]

    async def save_to_db(self, data: List[Dict]) -> None:
        folder_path = "chat_history"
        os.makedirs(folder_path, exist_ok=True)
        if self.current_chat_name:
             file_path = os.path.join(folder_path, f'{self.current_chat_name}')
             with open(file_path, 'w') as f:
                json.dump(data, f)
        else:
            response = await self.llm.arun("summarize this topic in maximum 5 words")
            print(response)
            file_path = os.path.join(folder_path, f'{response}.json')
            with open(file_path, 'w') as f:
                json.dump(data, f)

    def load_from_db(self, filename: str) -> List[Dict]:
        folder_path = "chat_history"
        file_path = os.path.join(folder_path, f'{filename}')
        with open(file_path, 'r') as f:
            return json.load(f)

    def messages_from_dict(self, data: List[Dict]) -> List:
        messages = []
        for m in data:
            if m['type'] == 'HumanMessage':
                messages.append(HumanMessage(content=m['content']))
            elif m['type'] == 'AIMessage':
                messages.append(AIMessage(content=m['content']))
        return messages

    async def load_chat_history(self, filename: str) -> None:
        self.thinking = True
        self.chat_messages.refresh()
        self.current_chat_name = filename
        self.llm.memory.clear()
        self.messages.clear()
        retrieved_messages = self.messages_from_dict(self.load_from_db(filename))
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        retrieved_memory = ConversationBufferMemory(chat_memory=retrieved_chat_history)
        self.llm = ConversationChain(llm=ChatOpenAI(model_name="mistral-7b-instruct", openai_api_key='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', openai_api_base="https://api.perplexity.ai"), memory=retrieved_memory)
        with get_openai_callback() as cb:
            response = await self.llm.arun("hi")
            print(response)
        self.messages = [('You', message.content) if isinstance(message, HumanMessage) else ('GPT', message.content) for message in retrieved_messages]
        #self.chatloaded = True
        self.thinking = False
        self.chat_messages.refresh()



chat_app = ChatApp()


chat_app = ChatApp()

@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        await chat_app.send(text)

    async def handle_new_chat():
        await chat_app.clear()
        chat_app.chat_history_grid.refresh()
    
    
    
    
    await client.connected()
 

    with ui.header(fixed=False).classes('items-center p-0 px-1 h-[6vh] no-wrap gap-0').style('box-shadow: 0 2px 4px').classes('bg-slate-100'):
        ui.button(on_click=lambda: drawer.toggle(), icon='menu').props('flat color=black')
        ui.label('Chat to LLM 💬').on("click", lambda: ui.open("/")).classes("cursor-pointer w-full text-black text-base font-semibold md:text-[2rem]")
    
    with ui.left_drawer(bottom_corner=True).style('background-color: #d7e3f4') as drawer:
        with ui.column().classes("w-full items-center"):
            ui.button(icon="add", on_click=handle_new_chat).props("rounded")
        with ui.expansion("Settings"):
            ui.label("Model").classes("pt-5")
            select = ui.select(["llama-2-70b-chat", "llama-2-13b-chat", "codellama-34b-instruct", "mistral-7b-instruct"], value="mistral-7b-instruct", on_change=lambda e: chat_app.on_value_change(ename=e.value)).classes("bg-slate-200")
            ui.label("Temperature").classes("pt-5")
            slider = ui.slider(min=0, max=2, step=0.1, value=5,on_change=lambda e: chat_app.on_value_change(etemp=e.value)).props("label-always")
        ui.separator().classes("bg-black")
        ui.label("Tokens Used").classes("pt-3")
        ui.label("0").bind_text_from(chat_app,"tokens_used").classes("pt-1")
        chat_app.chat_history_grid()
        

    with ui.column().classes('w-full items-stretch'):
        with ui.row().classes("items-center justify-center bg-slate-100"):
            ui.label("").bind_text_from(chat_app,"current_chat_name")
            ui.icon("delete", size="40px").bind_visibility_from(chat_app,"current_chat_name").on("click",ui.notify("hi"))
        await chat_app.chat_messages()


    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')



ui.run(title='Chat with GPT-3 (example)')