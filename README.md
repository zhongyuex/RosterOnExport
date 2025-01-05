# RosterOn to Google Calendar

This project automates the process of fetching your roster from RosterOn, parsing it, and synchronizing it with your Google Calendar from the earliest event entry in the current RosterOn.

## Prerequisites
Before running the script, ensure you have the following:

1. **Python 3.7 or later**
   - [Download Python](https://www.python.org/downloads/)
2. **Required Python Libraries**
   - Install dependencies using:
     ```bash
     pip install google-auth google-auth-oauthlib google-api-python-client bs4 ics requests pytz
     ```
3. **Google Calendar API Access**
   - Go to Google Cloud Console:
      * Select your project or create a new one.
   - Enable Google Calendar API:
     * Go to APIs & Services > Library.
     * Search for "Google Calendar API" and enable it.
   - Create OAuth 2.0 Client ID:
     * Go to APIs & Services > Credentials.
     * Click Create Credentials > OAuth Client ID.
     * Choose Desktop as the application type.
     * Add http://localhost/8080/ as an authorized redirect URI.
   - Download Credentials:
     * Once created, download the secret file as `gcal_credentials.json` and save it in your project directory.
4. **Create a designated Google Calendar**
   - Each update using this script will remove any calendar item that is not in sync with RosterOn. Please do not create your own event in this calendar if you want to use this script repeatedly.
   - Get your calendar ID from calendar setting - Integrate calendar. Save calendar ID as `calendarID.txt` in your project directory.

## Setup Instructions

### Step 1: Clone the Repository
Clone or download this repository to your computer:
```bash
git clone https://github.com/zhongyuex/RosterOnExport.git
cd RosterOnExport
```

### Step 2: Prepare Files
1. Ensure the Google API secret file is saved as `gcal_credentials.json` in the project directory.
2. Ensure the chosen calendar has a `calendarID.txt` file in the project directory (or use `primary` if you prefer to use your primary calendar).
3. Create a `RosterOn_credentials.json` file with your RosterOn username and password in the following format:
   ```json
   {
       "username": "your_username",
       "password": "your_password"
   }
   ```

### Step 3: Run the Script
Run the script to fetch, parse, and synchronize your roster:
```bash
python gcal_sync.py
```

### Step 4: Verify Google Calendar
Check your Google Calendar to ensure the roster events have been added and synchronized correctly.

## Script Details

### Main Functions

- **`authenticate_google_calendar`**
  Authenticates with Google Calendar API and returns the API service object.

- **`fetch_roster`**
  Logs into RosterOn and saves the roster page as `source.html`.

- **`read_roster`**
  Parses `source.html` and creates a `Calendar` object from the `ics` library.

- **`update_google_calendar`**
  Compares the roster events with existing Google Calendar events and override all existing event with most up-to-date roster fetched from RosterOn.

## Notes
- Existing events in the Google Calendar are updated or deleted as necessary to ensure synchronization.
- Please do not add your own events to the selected calendar because they will be deleted each time you run this script.

