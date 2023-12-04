from nicegui import ui, app
import os
from typing import Optional
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv


# Ein einfacher Benutzername-Passwort-Speicher. In einer echten Anwendung würden Passwörter gehasht und nicht im Klartext gespeichert.
load_dotenv("var.env")#load environmental variables
predefined_password = os.environ.get('PASSWORD')


@ui.page('/login')
# Definition der Anmeldeseite
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:
        # Überprüfen, ob das eingegebene Passwort mit dem vordefinierten Passwort übereinstimmt
        if password.value == predefined_password:
            # Aktualisieren des Benutzerstatus auf authentifiziert
            app.storage.user.update({'authenticated': True})
            # Weiterleitung des Benutzers zur ursprünglichen Seite oder zur Hauptseite, wenn keine ursprüngliche Seite gespeichert ist
            ui.open(app.storage.user.get('referrer_path', '/'))
        else:
            # Anzeigen einer Fehlermeldung, wenn das Passwort falsch ist
            ui.notify('Wrong password', color='negative')

    # Wenn der Benutzer bereits authentifiziert ist, wird er zur Hauptseite umgeleitet
    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        # Eingabefeld nur für das Passwort
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        # Schaltfläche zum Einloggen
        ui.button('Log in', on_click=try_login)