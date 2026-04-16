"""
One-time script to get a Gmail OAuth2 refresh token.
Run this locally ONCE, then store the output in Railway environment variables.

Usage:
    python get_gmail_token.py
"""
import urllib.parse
import urllib.request
import json

print("=== Gmail OAuth2 Token Setup ===\n")
client_id = input("Paste your Client ID: ").strip()
client_secret = input("Paste your Client Secret: ").strip()

auth_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={urllib.parse.quote(client_id)}"
    "&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
    "&response_type=code"
    "&scope=https://www.googleapis.com/auth/gmail.send"
    "&access_type=offline"
    "&prompt=consent"
)

print(f"\n1. Open this URL in your browser:\n\n{auth_url}\n")
print("2. Sign in with jessestorm1987@gmail.com and click Allow.")
code = input("3. Paste the code shown: ").strip()

data = urllib.parse.urlencode({
    "code": code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
with urllib.request.urlopen(req) as resp:
    tokens = json.loads(resp.read())

print("\n=== Set these in Railway environment variables ===\n")
print(f"GMAIL_USER=jessestorm1987@gmail.com")
print(f"GMAIL_CLIENT_ID={client_id}")
print(f"GMAIL_CLIENT_SECRET={client_secret}")
print(f"GMAIL_REFRESH_TOKEN={tokens['refresh_token']}")
