import mysql.connector
from dotenv import load_dotenv
from datetime import datetime, timedelta
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

    def insert_med_record(self, user_id, medication_name, dosage, schedule_type, interval_hours, start_time):
        cursor = self.db.cursor()
        
        try:
            # Start a transaction
            self.db.start_transaction()
            
            # Insert into medication_schedule
            med_sql = """INSERT INTO medication_schedule 
                        (user_id, name, dosage, schedule_type, interval_hours, start_time) 
                        VALUES (%s, %s, %s, %s, %s, %s)"""
            med_val = (user_id, medication_name, dosage, schedule_type, interval_hours, start_time)
            cursor.execute(med_sql, med_val)
            
            # Get the last inserted id (medication_id)
            medication_id = cursor.lastrowid

            # Calculate the first scheduled time
            current_date = datetime.now().date()
            start_datetime = datetime.combine(current_date, datetime.strptime(start_time, '%H:%M').time())

            # Insert into tracker
            tracker_sql = """INSERT INTO tracker 
                             (user_id, schedule_type, schedule_id, scheduled_time, status) 
                             VALUES (%s, %s, %s, %s, %s)"""
            
            # Loop to insert multiple tracking entries for 24 hours
            scheduled_times = []
            end_datetime = start_datetime + timedelta(hours=24)
            while start_datetime < end_datetime:
                tracker_val = (user_id, 'medication', medication_id, start_datetime, 'pending')
                cursor.execute(tracker_sql, tracker_val)
                scheduled_times.append(start_datetime.strftime('%H:%M'))
                
                # Add interval hours for the next entry
                start_datetime += timedelta(hours=interval_hours)
            
            # Commit the transaction
            self.db.commit()

            print(f"Tracking records inserted for times: {scheduled_times}")
            
        except mysql.connector.Error as err:
            # If an error occurs, roll back the transaction
            self.db.rollback()
            print(f"An error occurred: {err}")
            return None
        
        finally:
            cursor.close()

# user_id = 1
# medication_name = 'Paracetamol'
# dosage = '81mg'
# schedule_type = 'interval'
# interval_hours = 6
# start_time = '08:00'
# mydb = DBLogic()
# mydb.insert_med_record(user_id, medication_name, dosage, schedule_type, interval_hours, start_time)

    def insert_vitals_record(self,user_id, vitals, schedule_type, interval_hours, start_time):
        cursor = self.db.cursor()
        try:
            sql = "INSERT INTO vitals_schedule (user_id, name, schedule_type, interval_hours, start_time) VALUES (%s, %s, %s, %s, %s)"
            val = (user_id, vitals, schedule_type, interval_hours, start_time)
            cursor.execute(sql, val)
            # Get the last inserted id (medication_id)
            vitals_id = cursor.lastrowid

            # Calculate the first scheduled time
            current_date = datetime.now().date()
            start_datetime = datetime.combine(current_date, datetime.strptime(start_time, '%H:%M').time())

            # Insert into tracker
            tracker_sql = """INSERT INTO tracker 
                             (user_id, schedule_type, schedule_id, scheduled_time, status) 
                             VALUES (%s, %s, %s, %s, %s)"""
            
            # Loop to insert multiple tracking entries for 24 hours
            scheduled_times = []
            end_datetime = start_datetime + timedelta(hours=24)
            while start_datetime < end_datetime:
                tracker_val = (user_id, 'vitals', vitals_id, start_datetime, 'pending')
                cursor.execute(tracker_sql, tracker_val)
                scheduled_times.append(start_datetime.strftime('%H:%M'))
                
                # Add interval hours for the next entry
                start_datetime += timedelta(hours=interval_hours)

            self.db.commit()
            print(f"Tracking records inserted for times: {scheduled_times}")
            
        except mysql.connector.Error as err:
            # If an error occurs, roll back the transaction
            self.db.rollback()
            print(f"An error occurred: {err}")
            return None
        
        finally:
            cursor.close()
        
# user_id = 1
# vitals = 'Temperature'
# schedule_type = 'interval'
# interval_hours = 4
# start_time = '08:00'
# mydb = DBLogic()
# mydb.insert_vitals_record(user_id, vitals, schedule_type, interval_hours, start_time)

# to get the daily schedule for the day 
    def get_daily_schedule(self, user_id):
        cursor = self.db.cursor(dictionary=True)
        sql = """
        SELECT 
            t.schedule_type,
            t.scheduled_time,
            t.status,
            CASE 
                WHEN t.schedule_type = 'medication' THEN ms.name
                WHEN t.schedule_type = 'vitals' THEN vs.name
            END AS name,
            CASE 
                WHEN t.schedule_type = 'medication' THEN ms.dosage
            END AS dosage
        FROM 
            tracker t
        LEFT JOIN 
            medication_schedule ms ON t.schedule_id = ms.id AND t.schedule_type = 'medication'
        LEFT JOIN 
            vitals_schedule vs ON t.schedule_id = vs.id AND t.schedule_type = 'vitals'
        WHERE 
            t.user_id = %s AND DATE(t.scheduled_time) = CURDATE()
        ORDER BY 
            t.scheduled_time
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
# mydb = DBLogic()
# user_id = 1
# schedule = mydb.get_daily_schedule(user_id)
# print(schedule)
