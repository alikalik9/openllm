from dotenv import load_dotenv
import os
from nicegui import Client, ui, events, app
from chat import ChatApp
from embeddings import Embedding
#import user
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from authmiddleware import AuthMiddleware
import login_page


#embedding = Embedding()

# Eine Liste von Routen, die nicht authentifiziert werden müssen.

load_dotenv("var.env")#load environmental variables

with open('perplexity_model_list.txt', 'r') as file1, open('openai_model_list.txt', 'r') as file2:
    models = eval(file1.read()) + eval(file2.read())


@ui.page('/')
async def main(client: Client):
    chat_app = ChatApp()
    async def send() -> None:
        """triggers the send functiin of the chatapp class"""

        message = textarea.value
        textarea.value=""
        await chat_app.send(message)
  
    @ui.refreshable
    def embeddinglist():
        """
       Ui for the list of files used for the embedding
        """
        current_directory = os.getcwd()
        embedding_files = os.path.join(current_directory, 'embedding_files')
        if not os.path.exists(embedding_files):
            # If the directory doesn't exist, create it
            os.makedirs(embedding_files)
        embedding_filenames = [f for f in os.listdir(embedding_files)]
        ui.label("Your Uploaded Files").bind_visibility(embedding_switch,"value")
        with ui.column().classes("h-1/2 overflow-y-scroll bg-white cursor-pointer").bind_visibility_from(embedding_switch,"value"):
            with ui.element('q-list').props('bordered separator').classes("overflow-y-scroll w-full"):
                for filename in embedding_filenames:
                    with ui.element('q-item').classes("pt-2"): #chatlist
                        with ui.element('q-item-section'): #name of the chat
                            ui.label(filename)

    async def handle_new_chat():
        """Driggers the clear function of the chatapp class"""
        textarea.set_value("")
        await chat_app.clear()
        chat_app.chat_history_grid.refresh()

    async def handle_upload(e: events.UploadEventArguments):
        """Function for creating the files in the local directory after uploading them with ui.upload
            Also updates the embedding json index or creates it if not already created

            Parameters:
            e (events.UploadEventArguments): The upload event from nicegui
        """
        folder_path = "embedding_files"
        os.makedirs(folder_path, exist_ok=True)
        filename = e.name
        filedata = e.content.read()
        file_path = os.path.join(folder_path,filename)
        with open(file_path, "wb") as f:
            f.write(filedata)
        await embedding.create_index()
        embeddinglist.refresh()
        
    
    await client.connected()
 

    with ui.header(fixed=True).classes('items-center p-0 px-1 h-[6vh] gap-0 no-wrap').style('box-shadow: 0 2px 4px').classes('bg-neutral-100'):
        with ui.row().classes("w-full gap-0 h-full no-wrap items-center"):
            ui.button(on_click=lambda: drawer.toggle(), icon='menu').props('flat color=black')
            ui.label('Chat to LLM 💬').on("click", lambda: ui.open("/")).classes("cursor-pointer text-black w-2/3 text-base font-semibold md:text-[2rem]")
        ui.label("").bind_text_from(chat_app,"current_chat_name").classes("text-black overflow-scroll text-elipsis h-full w-full")
        ui.button(on_click=lambda: (app.storage.user.clear(), ui.open('/login')), icon='logout').props('outline round')
                ###Left drawer with all the settings###
    with ui.left_drawer(bottom_corner=True).classes("bg-neutral-100") as drawer:
        with ui.column().classes("w-full items-center"):
            embedding_switch = ui.switch("Chat with your Data",on_change=lambda e: chat_app.on_value_change(embedding_switch=e.value)).bind_value_from(chat_app,"embedding_switch")
            ui.button(icon="add", on_click=handle_new_chat, color="slate-400").props("rounded")
        with ui.expansion("Settings").classes("w-full"):
            ui.label("Model").classes("pt-5")
            models_select = ui.select(models, value=app.storage.user.get('last_model', models[0]), on_change=lambda e: chat_app.on_value_change(ename=e.value)).classes("bg-slate-200 w-full")
            ui.label("Temperature").classes("pt-5")
            slider = ui.slider(min=0, max=2, step=0.1, value=0.1,on_change=lambda e: chat_app.on_value_change(etemp=e.value)).props("label-always")
        with ui.column().classes("w-full no-wrap justify-center items-center pt-5"):
            with ui.row():
                ui.label("Tokens Used:")
                ui.label("").bind_text_from(chat_app,"tokens_used").classes("pb-2")
            with ui.row():
                ui.label("Total Cost:")
                ui.label("").bind_text_from(chat_app,"total_cost").classes("pb-2")
        ui.label("Chat History").classes("pt-4 pb-2 text-xl").bind_visibility_from(embedding_switch,"value", value=False)
        chat_app.chat_history_grid()
        embeddinglist()
        ui.label("Upload more Files").classes("pt-4 bp-4").bind_visibility_from(embedding_switch,"value")
        ui.upload(on_upload= handle_upload, multiple=True, auto_upload=True).classes("w-full").props('color=black accept=".pdf,.txt"').bind_visibility_from(embedding_switch,"value")        

                
    with ui.column().classes('w-full items-stretch items-center justiy-center'):     
        await chat_app.chat_messages()


    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if os.environ.get('OPEN_API_KEY') != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            with ui.textarea(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center') as textarea:
                ui.button(color='blue-8', on_click=send, icon='send').props('flat dense').bind_visibility_from(textarea, 'value')
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')

login_page
# Hinzufügen der AuthMiddleware zur Anwendung
app.add_middleware(AuthMiddleware)
ui.run(title='Chat with LLM', favicon="🤖", reconnect_timeout = 200, storage_secret = os.getenv("STORAGE_SECRET"))