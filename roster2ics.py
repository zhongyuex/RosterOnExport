from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
import json

# Read the HTML file
html_file = "source.html"
with open(html_file, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Parse events
events = []
for divider in soup.find_all("li", {"data-role": "list-divider"}):
    date_text = divider.text.strip().split(" - ")[0]
    details = divider.find_next_sibling("li")
    if details:
        time_row = details.find("tr").find("td").text.strip()
        on_call = "oncall" in time_row.lower()
        if on_call:
            time_row = time_row.lower().replace("oncall", "").strip("() ")
        time_parts = time_row.split(" - ")
        description = details.find_all("tr")[1].text.strip()
        role = details.find_all("tr")[2].text.strip()
        
        # Create a dictionary for this event
        events.append({
            "date": date_text,
            "start_time": time_parts[0],
            "end_time": time_parts[1],
            "description": description,
            "role": role
        })

# Save the events as a JSON file
json_file = "./roster.json"
with open(json_file, "w", encoding="utf-8") as file:
    json.dump(events, file, indent=4)
print(f"JSON file saved to {json_file}")

# Create the calendar
cal = Calendar()

# Define Melbourne timezone
melbourne_tz = pytz.timezone("Australia/Melbourne")

for event in events:
    # Parse date and time
    start_datetime = melbourne_tz.localize(
        datetime.strptime(f"{event["date"]} {event['start_time']}", "%a %d/%m/%Y %H:%M")
        )
    end_datetime = melbourne_tz.localize(
        datetime.strptime(f"{event["date"]} {event['end_time']}", "%a %d/%m/%Y %H:%M")
        )
    # Handle cases where the end time is on the next day (e.g., night shifts)
    if end_datetime <= start_datetime:
        end_datetime += timedelta(days=1)

    # Create and add the event to the calendar
    cal_event = Event()
    cal_event.name = event["description"]
    cal_event.description = event["role"]

    cal_event.begin = start_datetime
    cal_event.end = end_datetime
    # Set all-day event for annual leave
    if "annual leave" == event["description"].lower():
        cal_event.make_all_day()

    cal.events.add(cal_event)

# Save the .ics file
ics_file = "./roster.ics"
with open(ics_file, "w", encoding="utf-8") as file:
    file.writelines(cal)

print(f"Calendar saved to {ics_file}")
