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

    """
    Inserts signup data into the database.
    Username should not exceed 100 characters and password should be hashed into binary beforehand
    and converted to hexadecimal in string form to be inserted into the database.
    """
    def insert_signup_info(self, username, pwhash):
        cursor = self.db.cursor()
        # TODO account for edge cases, i.e. person alr exists, incompatible data type
        sql = "INSERT INTO patient_id (name, pw_hash) VALUES (%s, %s)"
        val = (username, pwhash)
        cursor.execute(sql, val)

        self.db.commit()

    """
    Retrieves password from the db with the input of a given username, 
    checking of validity to be left to the parent logic.
    input: username in string form.
    returns: password hash as a string.
    """
    def get_login_pwhash(self, username):
        cursor = self.db.cursor()
        sql = "SELECT pw_hash FROM patient_id WHERE name = %s"
        val = (username,)
        cursor.execute(sql, val)
        result = cursor.fetchone() # fetch only 1 record
        return result[0]

# below commands for testing, uncomment to use
# mydb = DBLogic()
# mydb.insert_signup_info("Amy", "Amelia")
# print(mydb.get_login_pwhash("Amy"))