from datetime import datetime, timedelta
from DBLogic import DBLogic
from collections import defaultdict
# from firebase.firebase import FirebaseMessenger

db = DBLogic()
class ScheduleChecker:
    #def __init__(self):
        #self.firebase_messenger = FirebaseMessenger()

    def check_and_send_notifications(self):
        user_id = 1  
        due_schedules = self.get_due_schedules(user_id)
        condensed_notifications = self.condense_schedules(due_schedules)
        print(f"Found {len(condensed_notifications)} condensed notifications")
        
        for notification in condensed_notifications:
            #self.send_firebase_notification(notification)
            #self.send_chatbot_reminder(notification)
            # Mark all schedules in this notification as notified
            for schedule in notification['schedules']:
                self.mark_as_notified(schedule['type'], schedule['scheduled_time'])
            
            # For testing purposes
            self.print_notification(notification)

    def get_due_schedules(self, user_id):
        schedules = db.get_daily_schedule(user_id)
        current_time = datetime.now()
        #current_time = datetime(2025, 3, 2, 15, 2, 40)
        print(f"Retrieved {len(schedules)} schedules")

        due_schedules = []
        for entry in schedules:
            scheduled_time = entry['scheduled_time']
            if current_time - timedelta(hours=1) <= scheduled_time <= current_time and entry['status'] != 'notified':
                due_schedules.append({
                    'type': entry['schedule_type'],
                    'scheduled_time': scheduled_time,
                    'status': entry['status'],
                    'name': entry['name'],
                    'dosage': entry['dosage']
                })
        return due_schedules
    
    def condense_schedules(self, due_schedules):
        grouped_schedules = defaultdict(lambda: defaultdict(list))
        
        for schedule in due_schedules:
            time_key = schedule['scheduled_time'].strftime('%Y-%m-%d %H:%M')
            schedule_type = schedule['type']
            grouped_schedules[time_key][schedule_type].append(schedule)
        
        condensed_notifications = []
        
        for time_key, type_schedules in grouped_schedules.items():
            for schedule_type, schedules in type_schedules.items():
                if len(schedules) > 1:
                    title = f"{schedule_type.capitalize()} Reminder"
                    body = f"Time for your {schedule_type} at {time_key}:\n"
                    for schedule in schedules:
                        body += f"- {schedule['name']}"
                        if schedule['dosage']:
                            body += f" ({schedule['dosage']})"
                        body += "\n"
                    condensed_notifications.append({
                        "title": title, 
                        "body": body.strip(),
                        "schedules": schedules
                    })
                else:
                    schedule = schedules[0]
                    title = f"{schedule_type.capitalize()} Reminder"
                    body = f"Time for your {schedule['name']} at {time_key}"
                    if schedule['dosage']:
                        body += f" - Dosage: {schedule['dosage']}"
                    condensed_notifications.append({
                        "title": title, 
                        "body": body,
                        "schedules": schedules
                    })
        
        return condensed_notifications

    def mark_as_notified(self, schedule_type, scheduled_time):
        user_id = 1
        db.mark_as_notified(user_id, schedule_type, scheduled_time)
    
    # def send_firebase_notification(self, notification):
    #     #Send notification using the Firebase
    #     # update the sendtotoken function to handle all the input variables
    #     #user_token = db.get_user_fcm_token(user_id=1)  # Implement this
    #     user_token = 'f3uGV-hbTbGAxdD27cFPmU:APA91bH0MblMqbC44ZLL9Rx74yAkC8u_KCUQ9DzQWYbOvcaeY01hLjMM6Euge5oP-d9TKZEPMICkpljyIy2J_HpZwNz8lkFL505ICVItyo9QzxhzJ2AMEx8'
        
    #     # Use the class instance created in __init__
    #     self.firebase_messenger.sendToToken(
    #         title=notification['title'],
    #         body=notification['body'],
    #         registration_token=user_token
    #     )

    # For testing purposes
    def print_notification(self, notification):
        print(f"Notification would be sent: Title: {notification['title']}, Body: {notification['body']}")
