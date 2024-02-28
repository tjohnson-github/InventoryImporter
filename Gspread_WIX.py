
import pickle
import gspread
from google.oauth2.service_account import Credentials
from decimal import *
from googleapiclient.discovery import build

def authGspread():

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    SERVICE_ACCOUNT_FILE ="C:\\Users\\Andrew\\source\\repos\\jfgcphotos-e815c44a79c2.json"

    credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    gc = gspread.authorize(credentials)

    return gc
 

def createFolder(name):


    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    SERVICE_ACCOUNT_FILE ="C:\\Users\\Andrew\\source\\repos\\jfgcphotos-e815c44a79c2.json"

    credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, fields="id").execute()

def addPendingWixProductsToSharedDrive(title):
    """
    Creates the Sheet the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """

    gc  =   authGspread()

    try:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = gc.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId') \
            .execute()
        print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
        return spreadsheet.get('spreadsheetId')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def createSheetAndPopulate(sheetName,entries_to_add,folderID):

    # Assumes sheet with correct header is already present:

    gc = authGspread()

    try:
        sh = gc.create(sheetName, folder_id=folderID)
        wk = sh.sheet1

        try:
            wk.insert_rows(entries_to_add)
        except Exception as ee:
            raise Exception(f"Cannot Print to {sheetName}:\t{e}")

    except Exception as e:
        print(f"Cannot Create {sheetName}:\t{e}")

   

def test():
    
    from File_Operations import excel_to_list

    path = f"C:\\Users\\Andrew\\source\\repos\\VENDOR_FILES\\OUTPUT\\"

    filename = "Inventory-MiscKensFall2022-Kens-SQL Full-wix-NO_URL.xlsx"

    testList,error = excel_to_list(f"{path}{filename}")


    for x in testList[0]:
        print(x)
        print("\n")


    createSheetAndPopulate(filename,testList,folderID="1Dtx3OCtqH0WrD1-OQLJgEyoAdbSMntPI")

#if __name__=="__main__":
#    test()
