import csv
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Generate .ics calendar files from a CSV file.')
parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
args = parser.parse_args()

# Define the folder to save the .ics files
output_folder = "calendar_files"
os.makedirs(output_folder, exist_ok=True)

# Function to create an event with a reminder
def create_event(summary, start_date, end_date, description, reminder_date):
    event = Event()
    event.add('X-APPLE-DEFAULT-ALARM', 'FALSE')
    event.add('summary', summary)
    event.add('description', description)
    event.add('dtstart', datetime.strptime(start_date, '%Y-%m-%d').date())
    event.add('dtend', datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1))
    event.add('dtstamp', datetime.now())

    # Add a reminder if a reminder date is provided
    alarm = Alarm()
    alarm.add("action", "DISPLAY")
    alarm.add("description", f"Reminder: {summary}")
    trigger_date = datetime.strptime(reminder_date, "%Y-%-m-%d") if reminder_date else timedelta(minutes=0)
    alarm.add("trigger", trigger_date)
    alarm.add("duration", timedelta(minutes=0))  # No repeat
    alarm.add("repeat", 0)  # No default recurrence
    event.add_component(alarm)
    return event

# Read the CSV file
with open(args.csv_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        summary = row['Summary']
        start_date = row['Start Date']
        end_date = row['End Date']
        description = row['Description']
        reminder_date = row.get('Reminder Date', None)

        # Create a new calendar
        cal = Calendar()
        event = create_event(summary, start_date, end_date, description, reminder_date)
        cal.add_component(event)

        # Save the .ics file
        file_name = f"{summary.replace(' ', '_').replace(':', '_')}.ics"
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(cal.to_ical())

        print(f"Created {file_path}")

print("All calendar events created in the 'calendar_files' folder!")

