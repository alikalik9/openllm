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
from nicegui import Client, ui, events
from chat import ChatApp

API_KEY = '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'
OPEN_API_KEY = '^'
PPL_BASE = 'https://api.perplexity.ai'

chat_app = ChatApp()

@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        message = textarea.value
        textarea.value=""
        await chat_app.send(message)

    async def handle_new_chat():
        await chat_app.clear()
        chat_app.chat_history_grid.refresh()

    def handle_upload(e: events.UploadEventArguments):
        ui.notify(e.name)
        folder_path = "embedding_files"
        os.makedirs(folder_path, exist_ok=True)
        filename = e.name
        filedata = e.content.read()
        file_path = os.path.join(folder_path,filename)
        with open(file_path, "wb") as f:
            f.write(filedata)
        
    
    await client.connected()
 

    with ui.header(fixed=True).classes('items-center p-0 px-1 h-[6vh] no-wrap gap-0').style('box-shadow: 0 2px 4px').classes('bg-slate-100'):
        ui.button(on_click=lambda: drawer.toggle(), icon='menu').props('flat color=black')
        ui.label('Chat to LLM 💬').on("click", lambda: ui.open("/")).classes("cursor-pointer text-black  w-1/3 text-base font-semibold md:text-[2rem]")
        with ui.row().classes("w-full no-wrap gap-0"):
            ui.label("").bind_text_from(chat_app,"current_chat_name").classes("text-black overflow-hidden w-full")
    with ui.left_drawer(bottom_corner=True).style('background-color: #b3cde0') as drawer:
        with ui.column().classes("w-full items-center"):
            embedding_switch = ui.switch("Chat with your Data",on_change=lambda e: chat_app.on_value_change(embedding_switch=e.value)).bind_value_from(chat_app,"embedding_switch")
            ui.button(icon="add", on_click=handle_new_chat, color="slate-400").props("rounded")
        with ui.expansion("Settings"):
            ui.label("Model").classes("pt-5")
            select = ui.select(["gpt-3.5-turbo", "llama-2-70b-chat", "llama-2-13b-chat", "codellama-34b-instruct", "mistral-7b-instruct"], value="llama-2-70b-chat", on_change=lambda e: chat_app.on_value_change(ename=e.value)).classes("bg-slate-200")
            ui.label("Temperature").classes("pt-5")
            slider = ui.slider(min=0, max=2, step=0.1, value=0.1,on_change=lambda e: chat_app.on_value_change(etemp=e.value)).props("label-always")
        ui.label("Chat History").classes("pt-4 pb-2 text-xl").bind_visibility_from(embedding_switch,"value", value=False)
        chat_app.chat_history_grid()
        with ui.row().classes("w-full no-wrap justify-center pt-5"):
            ui.label("Tokens Used:")
            ui.label("").bind_text_from(chat_app,"tokens_used").classes("pb-2")
            ui.label("Total Cost:")
            ui.label("").bind_text_from(chat_app,"total_cost").classes("pb-2")
        ui.upload(on_upload=handle_upload, multiple=True,).classes("w-full").props("color=black accept=.pdf").bind_visibility_from(embedding_switch,"value")
        

                
    with ui.column().classes('w-full items-stretch items-center justiy-center'):     
        await chat_app.chat_messages()


    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            textarea = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')



ui.run(title='Chat with GPT-3 (example)')