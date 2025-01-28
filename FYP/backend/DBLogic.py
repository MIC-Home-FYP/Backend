import mysql.connector
from dotenv import load_dotenv
import os

class DBLogic:
    def __init__(self):
        load_dotenv()
        MYSQL_USERNAME = os.environ.get("MYSQL_USERNAME")
        MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
        self.db = mysql.connector.connect(
            host = "localhost", 
            user = MYSQL_USERNAME, 
            password = MYSQL_PASSWORD, 
            database = "patients"
        )
    
    def show_all_tables(self):
        cursor = self.db.cursor()
        cursor.execute("SHOW TABLES")
        for x in cursor:
            print(x)

# TODO: to be removed later after testing is completed
mydb = DBLogic()
mydb.show_all_dbs()