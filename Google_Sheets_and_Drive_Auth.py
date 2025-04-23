import gspread
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = None
gc = None
drive_service = None

def auth_drive():
    print("auth_drive")
    global drive_service
    if not drive_service:
        credentials = auth()
        drive_service = build("drive", "v3", credentials=credentials)
    return drive_service

def auth_gspread():
    global gc
    if not gc:
        credentials = auth()
        gc = gspread.authorize(credentials)
    return gc

def auth():

    global credentials

    if not credentials:

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            elif os.path.exists("credentials.json"):
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                credentials = flow.run_local_server(port=0)
            else:
                raise FileNotFoundError("""No credentials found.
1: Go to https://console.cloud.google.com/.
2: Create a project.
3: In APIs & Services > Enabled APIs & services, enable the Gmail API.
4: In APIs & Services > OAuth consent screen, choose User Type: Internal and add the https://www.googleapis.com/auth/spreadsheets and https://www.googleapis.com/auth/drive scopes.
5: In APIs & Services > Credentials > Create Credentials > OAuth client ID, choose Desktop app.
6: Download the JSON file and place it in this directory as credentials.json.""")

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(credentials.to_json())

        print("Authentication with Google successful.")

    return credentials