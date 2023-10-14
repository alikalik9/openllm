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
    """
    Initializes the ChatApp class.The class contains all the methods to send messages to the llm, get the response and also save the chat history in a json format.
    It also contains some ui.parts, the ui.chat_message for displaying the chat conversation and an aggrid for displaying the chat history
    """
    def __init__(self):
        self.llm = ConversationChain(llm=ChatOpenAI(model_name="mistral-7b-instruct", openai_api_key='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', openai_api_base="https://api.perplexity.ai", temperature="0.1"), memory=ConversationBufferMemory())
        self.messages = [] # var that will contain an conversation
        self.thinking = False #var for showing the spinner 
        self.total_tokens = 0 # var for counting the tokens
        self.current_chat_name = "" #name for the currently selected chat. will be filled when someone clicks on a chat in the aggrid

    def on_value_change(self, ename="mistral-7b-instruct", etemp="0.3"):
        """
        Changes the value of the model and temperature for the ConversationChain.

        Parameters:
        ename (str): The name of the model.
        etemp (str): The temperature for the model.
        """
        self.llm = ConversationChain(llm=ChatOpenAI(model_name=ename, temperature=etemp, openai_api_key='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', openai_api_base="https://api.perplexity.ai"))

    @ui.refreshable
    async def chat_messages(self) -> None:
        """
        Displays the chat messages in the UI. Looks for the messages in the self.messages dict
        """
        for name, text in self.messages:
            ui.chat_message(text=text, name=name, sent=name == 'You').props(f"bg-color={('teal' if name == 'You' else 'primary')} text-color=white").classes("rounded-lg text-lg")
        if self.thinking:
            ui.spinner("dots",size='3rem')
        await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', respond=False)
    
    @ui.refreshable
    def chat_history_grid(self): #function for the table with the chat history
        """
        Creates a grid for the chat history. Uses the aggrid. When clicking on a chat the load_chat_history function is invoked to load chat from json
        """

        current_directory = os.getcwd()
        json_directory = os.path.join(current_directory, 'chat_history')   
        json_filenames = [f for f in os.listdir(json_directory) if f.endswith('.json')] #list all json files in directory
        rowData = [{'filename': filename} for filename in json_filenames]

        with ui.column().classes("h-1/2 overflow-scroll bg-white cursor-pointer"):
            with ui.element('q-list').props('bordered separator'):
                for filename in json_filenames:
                    with ui.element('q-item').classes("pt-2"): #chatlist
                        with ui.element('q-item-section'): #name of the chat
                            ui.label(filename).on("click", lambda filename=filename: self.load_chat_history(filename))
                        with ui.element('q-item-section').props('side'): #delete button and opening the dialog
                            with ui.dialog() as dialog, ui.card():
                                ui.label('Are you sure you want to delete the chat?')
                                with ui.row():
                                    ui.button('Yes', on_click=lambda filename=filename: self.delete_chat(filename)).classes("bg-red")
                                    ui.button('No', on_click=dialog.close)
                            ui.icon('delete',color="red").on("click", dialog.open)
                        with ui.element('q-item-section').props('side'):
                            ui.icon("edit")

       



    async def send(self, text) -> None:
        """
        Sends a message to the chat. Appends the self.messages list with the new message, sends it to the llm using the self.llm.arun function
        also afte every sending the current chat is beeing updated in the json

        Parameters:
        text (str): The message to be sent. Text beeing given from the ui.input
        """
        self.thinking = True
        #message = text.value
        self.messages.append(('You', text))
        self.chat_messages.refresh()
        with get_openai_callback() as cb:
            response = await self.llm.arun(text)
        self.tokens_used = cb.total_tokens  # get the total tokens used
        print(self.tokens_used)
        self.messages.append(('GPT', response))
        await self.save_to_db(self.messages_to_dict(self.llm.memory.chat_memory.messages))# Update the chat history to the database
        self.chat_history_grid.refresh()
        self.thinking = False
        self.chat_messages.refresh()

    async def clear(self):
        """
        Clears the chat memory and messages to "open" a new chat
        """
        self.llm.memory.clear()
        self.messages.clear()
        self.current_chat_name=""
        self.tokens_used = "0"
        self.chat_messages.refresh()
        


    def messages_to_dict(self, messages: List) -> List[Dict]:
        """
        Helper function for saving the messages to json. Converts the chat messages to a dictionary.

        Parameters:
        messages (List): The list of messages.

        Returns:
        List[Dict]: The dictionary representation of the messages.
        """
        return [{'type': type(m).__name__, 'content': m.content} for m in messages]

    async def save_to_db(self, data: List[Dict]) -> None:
        """
        Saves the chat history to the database. It checks if the current chat is already in the directory (thorugh self.current_chat_name) and if yes just updates the json file. if the chat is not in the directory
        a new json file is created. a call to the llm done before to sum the chat in 5 words and this becomde the filename fpr the json file.

        Parameters:
        data (List[Dict]): The chat history to be saved.
        """
        folder_path = "chat_history"
        os.makedirs(folder_path, exist_ok=True)
        if self.current_chat_name:
             file_path = os.path.join(folder_path, f'{self.current_chat_name}')
             with open(file_path, 'w') as f:
                json.dump(data, f)
        else:
            response = await self.llm.arun("summarize the request in not more than 5 words.")
            print(response)
            file_path = os.path.join(folder_path, f'{response}.json')
            with open(file_path, 'w') as f:
                json.dump(data, f)

    def load_from_db(self, filename: str) -> List[Dict]:
        """
        Loads the chat history from the database. Helper function to get the content of the json

        Parameters:
        filename (str): The name of the file to be loaded.

        Returns:
        List[Dict]: The loaded chat history.
        """
        folder_path = "chat_history"
        file_path = os.path.join(folder_path, f'{filename}')
        with open(file_path, 'r') as f:
            return json.load(f)

    def messages_from_dict(self, data: List[Dict]) -> List:
        """
        Converts the dictionary representation of messages to the actual messages.

        Parameters:
        data (List[Dict]): The dictionary representation of the messages.

        Returns:
        List: The actual messages.
        """
        messages = []
        for m in data:
            if m['type'] == 'HumanMessage':
                messages.append(HumanMessage(content=m['content']))
            elif m['type'] == 'AIMessage':
                messages.append(AIMessage(content=m['content']))
        return messages

    async def delete_chat(self,filename):
        current_directory = os.getcwd()
        json_directory = os.path.join(current_directory, 'chat_history')
        file_path = os.path.join(json_directory,filename)
        os.remove(file_path)
        self.chat_history_grid.refresh()



    async def load_chat_history(self, filename: str) -> None:
        """
        Loads the chat history. Gets the content of the selected json file and passes it as a langchain history object to the llm

        Parameters:
        filename (str): The name of the file to be loaded.
        """
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
        self.tokens_used = cb.total_tokens
        self.messages = [('You', message.content) if isinstance(message, HumanMessage) else ('GPT', message.content) for message in retrieved_messages]
        self.thinking = False
        self.chat_messages.refresh()



chat_app = ChatApp()


chat_app = ChatApp()

@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        message = textarea.value
        textarea.value = ""
        await chat_app.send(message)

    async def handle_new_chat():
        await chat_app.clear()
        chat_app.chat_history_grid.refresh()
    
    
    
    
    await client.connected()
 

    with ui.header(fixed=False).classes('items-center p-0 px-1 h-[6vh] no-wrap gap-0').style('box-shadow: 0 2px 4px').classes('bg-slate-100'):
        ui.button(on_click=lambda: drawer.toggle(), icon='menu').props('flat color=black')
        ui.label('Chat to LLM 💬').on("click", lambda: ui.open("/")).classes("cursor-pointer w-full text-black text-base font-semibold md:text-[2rem]")
    
    with ui.left_drawer(bottom_corner=True).style('background-color: #b3cde0') as drawer:
        with ui.column().classes("w-full items-center"):
            ui.button(icon="add", on_click=handle_new_chat).props("rounded")
        with ui.expansion("Settings"):
            ui.label("Model").classes("pt-5")
            select = ui.select(["llama-2-70b-chat", "llama-2-13b-chat", "codellama-34b-instruct", "mistral-7b-instruct"], value="mistral-7b-instruct", on_change=lambda e: chat_app.on_value_change(ename=e.value)).classes("bg-slate-200")
            ui.label("Temperature").classes("pt-5")
            slider = ui.slider(min=0, max=2, step=0.1, value=5,on_change=lambda e: chat_app.on_value_change(etemp=e.value)).props("label-always")
        ui.label("Tokens Used").classes("pt-3")
        ui.label("0").bind_text_from(chat_app,"tokens_used").classes("pt-1")
        ui.label("Chat").classes("pt-4 pb-2")
        chat_app.chat_history_grid()

                

    with ui.column().classes('w-full items-stretch'):
        await chat_app.chat_messages()


    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            textarea = ui.textarea(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')



ui.run(title='Chat with GPT-3 (example)', on_air="A2DCqSNCZ6Zbxv00")