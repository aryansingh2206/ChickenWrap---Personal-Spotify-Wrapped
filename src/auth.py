import os
import requests
import webbrowser
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPE = "user-read-recently-played user-top-read"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "/callback" in self.path:
            code = self.path.split("code=")[1]
            self.server.code = code
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth complete! You can close this window.")
        return

def get_auth_code():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    webbrowser.open(url)

    server = HTTPServer(("localhost", 8888), Handler)
    server.handle_request()
    return server.code

def get_tokens(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(TOKEN_URL, data=data)
    tokens = r.json()
    return tokens

if __name__ == "__main__":
    print("Opening browser for Spotify login...")
    code = get_auth_code()
    print("Received code. Exchanging for tokens...")

    tokens = get_tokens(code)

    with open(".env", "a") as f:
        f.write(f"\nACCESS_TOKEN={tokens['access_token']}")
        f.write(f"\nREFRESH_TOKEN={tokens['refresh_token']}")

    print("\nTokens saved to .env!")
