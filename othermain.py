from typing import List, Tuple, Union

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI

from nicegui import Client, ui

llm: Union[ConversationChain, None] = None 

messages: List[Tuple[str, str, str]] = []
thinking: bool = False


@ui.refreshable
async def chat_messages() -> None:
    for name, text in messages:
        ui.chat_message(text=text, name=name, sent=name == 'You')
    if thinking:
        ui.spinner(size='3rem').classes('self-center')
    await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', respond=False)


@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        global thinking
        message = text.value
        messages.append(('You', text.value))
        thinking = True
        text.value = ''
        chat_messages.refresh()
        await query(message)
        thinking = False

    async def query(message: str) -> None:
        global llm
        if llm is None:
            llm = ConversationChain(llm=ChatOpenAI(model_name="mistral-7b-instruct", openai_api_key='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', openai_api_base="https://api.perplexity.ai"))
            
        response = await llm.arun(message)
        messages.append(('Bot', response))
        chat_messages.refresh()

    anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
    ui.add_head_html(f'<style>{anchor_style}</style>')
    await client.connected()

    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
        await chat_messages()

    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.label('Chat with your AI').classes('text-2xl')

    with ui.left_drawer(bottom_corner=True).style('background-color: #d7e3f4'):
        ui.label('OpenAI private key').classes('text-lg mt-2')
        openai_key = ui.input(label='Key', placeholder='Provide your key here')

        ui.label('Exploration rate').classes('text-lg mt-2')
        exploration_slider = ui.slider(min=0, max=1, value=0.5, step=0.1)
        ui.label().bind_text_from(exploration_slider, 'value')

        ui.label('Maximum length of response').classes('text-lg mt-2')
        token_slider = ui.slider(min=100, max=4000, value=2000, step=10)
        ui.label().bind_text_from(token_slider, 'value')

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            text = ui.input(placeholder='message').props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')

ui.run(title='Chat with GPT-3 (example)')