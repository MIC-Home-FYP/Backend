from langchain.tools import Tool
import time
from datetime import datetime, timedelta
from DBLogic import DBLogic

db_logic = DBLogic()
current_time= datetime.now().strftime("%H:%M:%S")

class ReminderSubAgent:
    def __init__(self, user_id):
        self.db = db_logic
        self.user_id = user_id

    def get_formatted_schedule(self) -> str:
        """Retrieves and formats the daily schedule from database"""
        current_time = datetime.now()
        schedule = self.db.get_daily_schedule(self.user_id)
        if not schedule:
            return "No scheduled items for today"
            
        formatted = []
        for item in schedule:
            scheduled_time = item['scheduled_time']
            time_diff = scheduled_time - current_time
            
            if time_diff > timedelta():
                time_status = f"in {int(time_diff.total_seconds() / 60)} minutes"
            else:
                time_status = f"{int(abs(time_diff.total_seconds()) / 60)} minutes ago"
            
            entry = (
                f"{item['schedule_type'].title()} at {scheduled_time.strftime('%H:%M')}: "
                f"{item['name']} ({time_status})"
            )
            if item['dosage']:
                entry += f" - Dosage: {item['dosage']}"
            formatted.append(entry)
        print(formatted)
        return "\n".join(formatted)

def reminder_tool(agent: ReminderSubAgent) -> Tool:
    return Tool(
        name="patient_schedule",
        description="Access patient's daily medication and vital check schedule. "
                   "Use when asked about current and ending medications or health checks to provide daily schedule",
        func=lambda _: agent.get_formatted_schedule()
    )