
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client, app



unrestricted_page_routes = {'/login'}


# Eine Middleware-Klasse, die alle Anfragen abfängt und überprüft, ob der Benutzer authentifiziert ist.
class AuthMiddleware(BaseHTTPMiddleware):
    """Diese Middleware beschränkt den Zugriff auf alle NiceGUI-Seiten.

    Sie leitet den Benutzer zur Anmeldeseite weiter, wenn er nicht authentifiziert ist.
    """
    async def dispatch(self, request: Request, call_next):
        # Überprüfen, ob der Benutzer authentifiziert ist
        if not app.storage.user.get('authenticated', False):
            # Wenn der Benutzer nicht authentifiziert ist und versucht, auf eine geschützte Seite zuzugreifen, wird er zur Anmeldeseite umgeleitet.
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                # Speichern des ursprünglichen Pfades, um den Benutzer nach erfolgreicher Anmeldung dorthin zurückzuleiten.
                app.storage.user['referrer_path'] = request.url.path
                return RedirectResponse('/login')
        # Wenn der Benutzer authentifiziert ist oder versucht, auf eine nicht geschützte Seite zuzugreifen, wird die Anfrage normal verarbeitet.
        return await call_next(request)