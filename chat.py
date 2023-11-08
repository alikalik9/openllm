import json
import os
import shutil
import asyncio
from datetime import datetime
from typing import List, Dict
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.memory.chat_memory import ChatMessageHistory
from nicegui import ui
from embeddings import Embedding

API_KEY = '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'
OPEN_API_KEY = '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'
PPL_BASE = 'https://api.perplexity.ai'

class ChatApp(Embedding):
    """
    Initializes the ChatApp class.The class contains all the methods to send messages to the llm, get the response and also save the chat history in a json format.
    It also contains some ui.parts, the ui.chat_message for displaying the chat conversation and an aggrid for displaying the chat history
    """
    def __init__(self):
        super().__init__()  # Call the initializer of the parent class
        self.memory = ConversationBufferMemory()
        self.embedding_switch= False
        self.llm = ConversationChain(llm=ChatOpenAI(model_name="pplx-70b-chat-alpha", openai_api_key='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', openai_api_base="https://api.perplexity.ai", temperature="0.1"), memory=self.memory)
        self.messages = [] # var that will contain an conversation
        self.thinking = False #var for showing the spinner 
        self.tokens_used = 0 # var for counting the tokens
        self.total_cost = 0 #var for cost in usd
        self.current_chat_name = "" #name for the currently selected chat. will be filled when someone clicks on a chat in the aggrid
        self.api_key = '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'
        self.openai_api_key = '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'

    def on_value_change(self, ename="pplx-70b-chat-alpha", etemp="0.1", embedding_switch=False):
        """
        Changes the value of the model and temperature for the ConversationChain.

        Parameters:
        ename (str): The name of the model.
        etemp (str): The temperature for the model.
        """
        perplexity_models = ["llama-2-70b-chat", "pplx-70b-chat-alpha", "llama-2-13b-chat", "codellama-34b-instruct", "mistral-7b-instruct"]
        openai_models = ["gpt-3.5-turbo","gpt-4-1106-preview"]
        if ename in perplexity_models:
            self.llm = ConversationChain(llm=ChatOpenAI(model_name=ename, openai_api_key=self.api_key, openai_api_base="https://api.perplexity.ai", temperature=etemp), memory=ConversationBufferMemory())
        else:
            self.llm = ConversationChain(llm=ChatOpenAI(model_name=ename, openai_api_key=self.openai_api_key, temperature=etemp), memory=ConversationBufferMemory())
        self.embedding_switch = embedding_switch

    @ui.refreshable
    async def chat_messages(self) -> None:
        """
        Displays the chat messages in the UI. Looks for the messages in the self.messages dict
        """
        async def copy_code(text):
            escaped_text = text.replace("\\", "\\\\").replace("`", "\\`")
            await ui.run_javascript(f'navigator.clipboard.writeText(`{escaped_text}`)', respond=False)
            ui.notify("Text Copied!", type="positive")

        chatcolumn = ui.column().classes("w-full")
        for name, text in self.messages:
            #ui.chat_message(text=text, name=name, sent=name == 'You').props(f"bg-color={('teal' if name == 'You' else 'primary')} text-color=white").classes("rounded-lg text-lg")
            with chatcolumn:
                if name == 'You':
                    with ui.row().classes("w-full overflow-scroll bg-slate-100 no-wrap"):
                        ui.icon("download", size="40px").on("click" , lambda text=text, copy_code=copy_code: copy_code(text))
                        ui.markdown(text).classes("text-lg")
                        #ui.icon('content_copy', size='xl').classes('opacity-20 hover:opacity-80 cursor-pointer').on("click" , lambda text=text: copy_code(text))
                else:
                    with ui.row().classes("w-full no-wrap overflow-scroll bg-slate-200"):
                        ui.icon("person", size="40px")
                        ui.markdown(text).classes("w-full text-lg")
                    ui.icon('content_copy', size='xs').classes('opacity-20 hover:opacity-80 cursor-pointer pb-5').on("click" , lambda text=text: copy_code(text))

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
        if not os.path.exists(json_directory):
        # If the directory doesn't exist, create it
            os.makedirs(json_directory)  
        json_filenames = [f for f in os.listdir(json_directory) if f.endswith('.json')] #list all json files in directory

        # Create a list of tuples, each containing a filename and its corresponding timestamp
        timestamps_and_filenames = []
        for filename in json_filenames:
            with open(os.path.join(json_directory, filename), 'r') as f:
                data = json.load(f)
                timestamp = data['timestamp']
                timestamps_and_filenames.append((timestamp, filename))

        # Sort the list of tuples by the timestamp (in descending order)
        timestamps_and_filenames.sort(reverse=True)

        # Extract the sorted filenames
        sorted_filenames = [filename for timestamp, filename in timestamps_and_filenames]

        with ui.column().classes("h-1/2 overflow-y-scroll bg-white cursor-pointer").bind_visibility_from(self,"embedding_switch", value=False):
            with ui.element('q-list').props('bordered separator').classes("overflow-y-scroll"):
                for filename in sorted_filenames:
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
                        with ui.element('q-item-section').props('side'): #edit name button
                            with ui.dialog() as edit_dialog, ui.card().classes("w-1/2"):
                                ui.label('Enter the new name')
                                name_input = ui.input(on_change=lambda e: self.get_chat_name(e.value)).classes("w-full")
                                with ui.row():
                                    ui.button('Rename', on_click=lambda filename=filename: self.rename_chat(filename)).classes("bg-black")
                                    ui.button('Close', on_click=edit_dialog.close)
                            ui.icon("edit").on("click", edit_dialog.open)

    async def send(self, text) -> None:
        """
        Sends a message to the chat. Appends the self.messages list with the new message, sends it to the llm using the self.llm.arun function
        also afte every sending the current chat is beeing updated in the json

        Parameters:
        text (str): The message to be sent. Text beeing given from the ui.input
        """
        self.thinking = True
        self.chat_messages.refresh()
        current_directory = os.getcwd()
        embedding_dir = os.path.join(current_directory, 'embedding_files')   
        vector_dir = os.path.join(current_directory, "index_files")
        #message = text.value
        self.messages.append(('You', text))
        if self.embedding_switch is True:  ###if we are using embedding the chat history is not saved
            with get_openai_callback() as cb:
                response = await self.querylangchain(prompt=text)  ##using the langchain angent from the embeddings.py instead of a simple gpt call
                self.tokens_used = cb.total_tokens
                self.total_cost = round(cb.total_cost,6)  # get the total tokens used
                self.messages.append(('GPT', response))
                self.thinking = False
                self.chat_messages.refresh()
                #print(response)
        else:
            with get_openai_callback() as cb:  ##if we are not using embedding the chat history is saved
                response = await self.llm.arun(text)
                self.tokens_used = cb.total_tokens
                self.total_cost = cb.total_cost  # get the total tokens used
                self.messages.append(('GPT', response))
                await self.save_to_db(self.messages_to_dict(self.memory.chat_memory.messages))
                self.chat_history_grid.refresh()
                self.thinking = False
                self.chat_messages.refresh()
                #print(response)

            

    async def clear(self):
        """
        Clears the chat memory and messages to "open" a new chat
        """
        self.llm.memory.clear()
        self.memory.clear()
        self.messages.clear()
        self.current_chat_name=""
        self.tokens_used = "0"
        self.embedding_switch = False
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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_with_timestamp = {"timestamp": timestamp, "messages": data}
        if self.current_chat_name:
             file_path = os.path.join(folder_path, f'{self.current_chat_name}')
             with open(file_path, 'w') as f:
                json.dump(data_with_timestamp, f)
        else:
            chat_history_text = '\n'.join(f'{"You" if m["type"] == "HumanMessage" else "GPT"}: {m["content"]}' 
                                       for m in data)
            prompt_text = f"{chat_history_text}\n\nSummarize the above conversation with a descriptive name not longer than 5 words. Output only the name chosen."
            
            llm = ConversationChain(llm=ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=self.openai_api_key, temperature=0.1))
            response = await llm.arun(prompt_text)
            #response = datetime.now()
            print(response)
            file_path = os.path.join(folder_path, f'{response}.json')
            with open(file_path, 'w') as f:
                json.dump(data_with_timestamp, f)
            self.current_chat_name = f'{response}.json'

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
            data_with_timestamp=json.load(f)
        return data_with_timestamp["messages"]

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
        await self.clear()
        self.chat_history_grid.refresh()
    
    def get_chat_name(self,chat_name):
        self.chat_name = chat_name

    async def rename_chat(self, old_filename):
        print(old_filename + "old")
        current_directory = os.getcwd()
        json_directory = os.path.join(current_directory, 'chat_history')
        old_file_path = os.path.join(json_directory, old_filename)
        new_file_path = os.path.join(json_directory, self.chat_name+".json")
        
        if os.path.exists(old_file_path):
            shutil.move(old_file_path, new_file_path)
            ui.notify(f"Chat renamed from {old_filename} to {self.chat_name}.json",type="positive")
        else:
            ui.notify(f"No chat found with the name {old_filename}",type="negative")
        self.chat_history_grid.refresh()
    



    async def load_chat_history(self, filename: str) -> None:
        """
        Loads the chat history. Gets the content of the selected json file and passes it as a langchain history object to the llm

        Parameters:
        filename (str): The name of the file to be loaded.
        """
        self.thinking = True
        self.current_chat_name = filename
        # Clear existing messages and memory before loading new history
        self.messages = []  # Reset the messages list to be empty
        self.memory.clear()  # Clear the chat memory
        
        # Load saved messages from JSON file
        retrieved_messages = self.messages_from_dict(self.load_from_db(filename))
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        self.memory.chat_memory = retrieved_chat_history  # Update ConversationBufferMemory with loaded history
        
        # Directly set self.messages to the loaded messages only
        self.messages = [('You', m.content) if isinstance(m, HumanMessage) else ('GPT', m.content) for m in retrieved_messages]
        self.thinking = False
        self.chat_messages.refresh()

