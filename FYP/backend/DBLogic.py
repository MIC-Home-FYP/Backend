import mysql.connector
from dotenv import load_dotenv
import os

class DBLogic:
    def __init__(self):
        load_dotenv()
        MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        print(MYSQL_USERNAME)
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

    def insert_chat_interaction(self, user_id, message, sender):
            cursor = self.db.cursor()
            sql = "INSERT INTO chat_history (user_id, message, sender) VALUES (%s, %s, %s)"
            val = (user_id, message, sender)
            cursor.execute(sql, val)
            self.db.commit()
    def get_recent_user_conversations(self, user_id, limit=50):
            cursor = self.db.cursor()
            sql = "SELECT * FROM chat_history WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s"
            cursor.execute(sql, (user_id, limit))
            return cursor.fetchall()

# below commands for testing, uncomment to use
#mydb = DBLogic()
#mydb.insert_chat_interaction(1, "Hello", 'Human Message')
#mydb.insert_chat_interaction(1, "Hope you're doing well", 'AI Message')
#mydb.get_recent_user_conversations(1, 50)