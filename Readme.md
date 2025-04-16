# InventoryImporter
Previousely JFGC_ImportGUI repo Project DPG_311

## Building
1. Install python and pyinstaller
2. Run build.bat

## Installation
1. Install ODBC Driver 17 for SQL Server
2. Get credentials.json:
    1. Go to https://console.cloud.google.com/.
    2. Create a project.
    3. In APIs & Services > Enabled APIs & services, enable the Gmail API.
    4. In APIs & Services > OAuth consent screen, choose User Type: Internal and add the https://www.googleapis.com/auth/spreadsheets and https://www.googleapis.com/auth/drive scopes.
    5. In APIs & Services > Credentials > Create Credentials > OAuth client ID, choose Desktop app.
    6. Download the JSON file and place it in the same directory as InventoryImporter.exe.
3. Create a VENDOR_FILES folder with INPUT, STAGED, OUTPUT, and PROCESSED subfolders.
4. Run InventoryImporter.exe and enter the path to VENDOR_FILES in the Default Directories tab.