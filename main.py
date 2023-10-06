from typing import List, Tuple
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory
from nicegui import Client, ui

OPENAI_API_KEY = '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'

class ChatApp:
    def __init__(self):
        self.llm = ConversationChain(llm=ChatOpenAI(model_name="mistral-7b-instruct", openai_api_key='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', openai_api_base="https://api.perplexity.ai"), memory=ConversationBufferMemory())
        self.messages = []
        self.thinking = False

    def on_value_change(self, ename="mistral-7b-instruct", etemp="1"):
        self.llm = ConversationChain(llm=ChatOpenAI(model_name=ename, temperature=etemp, openai_api_key='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', openai_api_base="https://api.perplexity.ai"))

    @ui.refreshable
    async def chat_messages(self) -> None:
        for name, text in self.messages:
            ui.chat_message(text=text, name=name, sent=name == 'You').props(f"bg-color={('teal' if name == 'You' else 'primary')} text-color=white").classes("rounded-lg")
        if self.thinking:
            ui.spinner("dots",size='3rem')
        await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', respond=False)

    async def send(self, text) -> None:
        message = text.value
        self.messages.append(('You', text.value))
        self.thinking = True
        text.value = ''
        self.chat_messages.refresh()
        response = await self.llm.arun(message)
        self.messages.append(('GPT', response))
        self.thinking = False
        self.chat_messages.refresh()
    
    async def clear(self):
        self.messages.clear()
        self.chat_messages.refresh()
        self.llm.memory.clear()


chat_app = ChatApp()

@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        await chat_app.send(text)

    await client.connected()

    with ui.header(fixed=False).classes('items-center p-0 px-1 h-[6vh] no-wrap gap-0').style('box-shadow: 0 2px 4px').classes('bg-slate-100'):
        ui.button(on_click=lambda: drawer.toggle(), icon='menu').props('flat color=black')
        ui.label('Chat to LLM 💬').on("click", lambda: ui.open("/")).classes("cursor-pointer w-full text-black text-base font-semibold md:text-[2rem]")
    
    with ui.left_drawer(bottom_corner=True).style('background-color: #d7e3f4') as drawer:
        ui.button(icon="add", on_click=chat_app.clear).props("rounded")
        ui.label("Model").classes("pt-5")
        select = ui.select(["llama-2-70b-chat", "llama-2-13b-chat", "codellama-34b-instruct", "mistral-7b-instruct"], value="mistral-7b-instruct", on_change=lambda e: chat_app.on_value_change(ename=e.value)).classes("bg-slate-200")
        ui.label("Temperature").classes("pt-5")
        slider = ui.slider(min=0, max=2, step=0.1, value=5,on_change=lambda e: chat_app.on_value_change(etemp=e.value)).props("label-always")
        ui.separator().classes("bg-black")

    with ui.column().classes('w-full items-stretch'):
        await chat_app.chat_messages()


    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if OPENAI_API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')



ui.run(title='Chat with GPT-3 (example)')