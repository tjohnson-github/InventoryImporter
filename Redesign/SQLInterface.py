
import pyodbc

class SQLClient:

    server      =   '192.168.4.13'
    driver      =   '{ODBC Driver 17 for SQL Server}'
    username    =   'sa'
    password    =   'CounterPoint8'

    def __init__(self):
        try:
            #----------------
            conn_str=(';DRIVER='+self.driver+';SERVER='+self.server+';UID='+self.username+';PWD='+self.password)        
            print(conn_str)
            cnxn = pyodbc.connect(conn_str)
            cursor = cnxn.cursor()
            #----------------
            self.cnxn   = cnxn
            self.cursor = cursor
        except Exception as e:
            print ("_____ERROR_____")
            print ("Cursor object not initialized correctly. Please run Setup and retry.")
   
  