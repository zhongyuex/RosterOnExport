from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os
import requests
import json
import sys

# Redirect stdout and stderr to a log file
log_file = open("script.log", "a")  # Append mode to keep logs
sys.stdout = log_file
sys.stderr = log_file

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar(credentials_file="credentials.json"):
    """Authenticate and return the Google Calendar API service."""
    creds = None
    with open(credentials_file, "r") as file:
        credentials = json.load(file)
    client_secrets_file = credentials["gcp"]["client_secrets_file"]

    # Load existing credentials
    token_file = "token.json"
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for future use
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def fetch_roster(credentials_file="credentials.json"):
    """Fetch the RosterON HTML from the web and save it to a file."""
    LOGIN_URL = "https://rmhrosterweb.ssg.org.au/RosterOnProd/Mobile/Account/Login"

    # Load credentials
    with open(credentials_file, "r") as file:
        credentials = json.load(file)
    rosteron_credentials = credentials["rosteron"]

    # Start a session
    session = requests.Session()

    # Get the login page to retrieve any necessary tokens or cookies
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, "html.parser")

    # If there are CSRF tokens or other hidden fields, extract them
    csrf_token = soup.find("input", {"name": "__RequestVerificationToken"})
    if csrf_token:
        rosteron_credentials["__RequestVerificationToken"] = csrf_token["value"]

    # Send the POST request to log in
    response = session.post(LOGIN_URL, data=rosteron_credentials)

    # Check the response
    if response.status_code == 200:
        print("Login successful!")

        # Navigate to the roster page
        roster_url = "https://rmhrosterweb.ssg.org.au/RosterOnProd/Mobile/Roster/List?pageNo=1&row=1"
        roster_response = session.get(roster_url)

        if roster_response.status_code == 200:
            print("Successfully accessed the roster page!")
            roster_page = BeautifulSoup(roster_response.text, "html.parser")

            # Save the roster HTML to a file
            with open("source.html", "w", encoding="utf-8") as file:
                file.write(roster_page.prettify())

            print("Roster saved to source.html")
        else:
            print(f"Failed to access roster page. Status code: {roster_response.status_code}")
    else:
        print("Login failed. Check your credentials or the login process.")


def read_roster(html_file_path = "source.html"):
    """Parse the roster HTML file and return a Calendar object."""
    calendar = Calendar()
    melbourne_tz = pytz.timezone("Australia/Melbourne")

    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

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

                # Convert times to Melbourne timezone
                start_datetime = melbourne_tz.localize(
                    datetime.strptime(f"{date_text} {time_parts[0]}", "%a %d/%m/%Y %H:%M")
                )
                end_datetime = melbourne_tz.localize(
                    datetime.strptime(f"{date_text} {time_parts[1]}", "%a %d/%m/%Y %H:%M")
                )

                # Handle cases where the end time is on the next day (e.g., night shifts)
                if end_datetime <= start_datetime:
                    end_datetime += timedelta(days=1)

                # Create an event
                event = Event()
                event.name = description
                event.description = role

                # Handle annual leave as all-day events
                if "annual leave" in description.lower():
                    event.begin = start_datetime.date()
                    event.make_all_day()
                else:
                    event.begin = start_datetime
                    event.end = end_datetime

                calendar.events.add(event)
    return calendar

def update_google_calendar(service, calendar_id, calendar):
    """Update Google Calendar to match the given Calendar object using set operations."""
    if not calendar.events:
        print("No events to update.")
        return

    # Find the earliest event date
    earliest_event = min(calendar.events, key=lambda e: e.begin)
    start_date = earliest_event.begin.date()
    time_min = datetime.combine(start_date, datetime.min.time()).astimezone(pytz.UTC).isoformat()

    # List existing events from the earliest date onwards
    existing_events = service.events().list(calendarId=calendar_id, timeMin=time_min).execute().get('items', [])

    # Convert existing events into a set of keys (summary, start, end)
    existing_event_keys = {
        (
            e['summary'],
            e['start'].get('dateTime', e['start'].get('date')),
            e['end'].get('dateTime', e['end'].get('date'))
        )
        for e in existing_events
    }

    # Convert new events into a set of keys (summary, start, end)
    new_event_keys = {
        (
            event.name,
            event.begin.isoformat() if not event.all_day else event.begin.date().isoformat(),
            event.end.isoformat() if not event.all_day else (event.begin).date().isoformat()
        )
        for event in calendar.events
    }

    # Determine events to add
    events_to_add = new_event_keys - existing_event_keys
    # Determine events to delete
    events_to_delete = existing_event_keys - new_event_keys

    # Add new events
    for key in events_to_add:
        event = next(e for e in calendar.events if (
            e.name,
            e.begin.isoformat() if not e.all_day else e.begin.date().isoformat(),
            e.end.isoformat() if not e.all_day else (e.begin).date().isoformat()
        ) == key)

        new_event = {
            'summary': event.name,
            'start': {'dateTime': event.begin.isoformat()} if not event.all_day else {'date': event.begin.date().isoformat()},
            'end': {'dateTime': event.end.isoformat()} if not event.all_day else {'date': (event.begin).date().isoformat()},
            'description': event.description,
        }
        print("Inserting new event:", new_event)
        service.events().insert(calendarId=calendar_id, body=new_event).execute()

    # Delete old events
    for key in events_to_delete:
        event_to_delete = next(e for e in existing_events if (
            e['summary'],
            e['start'].get('dateTime', e['start'].get('date')),
            e['end'].get('dateTime', e['end'].get('date'))
        ) == key)

        print("Deleting event:", event_to_delete['summary'])
        service.events().delete(calendarId=calendar_id, eventId=event_to_delete['id']).execute()



def main():
    # Time stamp
    print(f"Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load credentials
    with open("credentials.json", "r") as file:
        calendar_id = json.load(file)["gcal"]["calendar_id"]

    # Fetch the roster HTML
    fetch_roster()

    # Read events from HTML file
    calendar = read_roster()

    # Authenticate Google Calendar API
    service = authenticate_google_calendar()
    print("Google service authenticated")

    # Update Google Calendar
    update_google_calendar(service, calendar_id, calendar)
    print("All Done")


if __name__ == "__main__":
    main()
