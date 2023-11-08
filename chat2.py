async def chat_messages(self) -> None:
        """
        Displays the chat messages in the UI. Looks for the messages in the self.messages dict
        """
       # async def copy_code(text):
         #   await ui.run_javascript('navigator.clipboard.writeText(`' + text + '`)', respond=False)
          #  ui.notify("Text Copied!",type="positive")

        chatcolumn = ui.column().classes("w-full")
        for name, text in self.messages:
            #ui.chat_message(text=text, name=name, sent=name == 'You').props(f"bg-color={('teal' if name == 'You' else 'primary')} text-color=white").classes("rounded-lg text-lg")
            with chatcolumn:
                if name == 'You':
                    with ui.row().classes("w-full bg-slate-100 no-wrap"):
                        #ui.icon("download", size="40px").on("click" , lambda text=text: copy_code(text))
                        ui.markdown(text).classes("text-lg")
                        #ui.icon('content_copy', size='xs').classes('absolute right-2 top-2 opacity-20 hover:opacity-80 cursor-pointer')
                else:
                    with ui.row().classes("no-wrap bg-slate-200"):
                        ui.icon("person", size="40px")
                        ui.markdown(text).classes("w-full text-lg")
        if self.thinking:
            ui.spinner("dots",size='3rem')
        await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', respond=False)