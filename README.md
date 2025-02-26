# RosterOn to Google Calendar
This project automates the process of fetching your roster from RosterOn, parsing it, and synchronizing it with your Google Calendar from the earliest event entry found in RosterOn.

The following instructions are for Google Calendar. Consider ics export (code in ``offline`` branch) for other calendars.

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
   - Download Credentials:
     * Once client ID has been created, download the secret file and save it somewhere.
4. **Create a designated Google Calendar**
   - Each update using this script will remove any calendar item that is not in sync with RosterOn. Please do not create your own event in this calendar if you want to use this script repeatedly.
   - Get your calendar ID from calendar setting -> Integrate calendar. Save this calendar ID somewhere.

## Setup Instructions

### Step 1: Download or clone the Repository
Clone or download this repository to your computer:
```bash
git clone https://github.com/zhongyuex/RosterOnExport.git
cd RosterOnExport
```

### Step 2: Prepare Credential Files
1. Create a new file `credentials.json` containing the following:
```json
{
    "gcp": {
        "client_secrets_file": **Paste the content of your secret file here**   ,
    "rosteron": {
        "username": **Enter your roster-on username here**   , 
        "password": **Enter your roster-on password here**
    },
    "gcal": {
        "calendar_id": **Paste your calendar ID here**
    }
}

```

### Step 3: Run the Script
Run the script to fetch, parse, and synchronize your roster:
```bash
python gcal_sync.py
```

### Step 4: Verify Output
1. Check the script output at `script.log`
2. Check your Google Calendar to ensure the roster events have been added and synchronized correctly.

## Script Details

### Main Functions

- **`authenticate_google_calendar`**
  Authenticate with Google Calendar API and return the API service object.
  Uses client secrets and token files for authentication.

- **`fetch_roster`**
  Fetch the RosterON HTML roster using the provided credentials and save it locally.
  Handles CSRF tokens and session management for secure login.

- **`read_roster`**
  Synchronize Google Calendar with the provided Calendar object.
  Adds, updates, or deletes events based on differences between the two, starting from the earliest time point provided by the RosterOn calendar.

- **`update_google_calendar`**
  Compares the roster events with existing Google Calendar events and override all existing event with most up-to-date roster fetched from RosterOn.



## Notes
- Existing events in the Google Calendar are updated or deleted as necessary to ensure synchronization.
- Please **DO NOT add your own events to the selected calendar** because they will be deleted each time you run this script.

# Windows Task Scheduler
Schedule the script to run once every few days at your local Windows computer

### Prerequisite
Create a new file `script.bat` containing the following:
```bat
cd "   **path to your repository** "
python gcal_sync.py
```

### Schedule the Task
1. Open Task Scheduler:
   - Press Win + S, type Task Scheduler, and hit Enter.
2. Create a New Task:
   - Click Create Task in the right-hand panel.
3. Configure the General Settings:
   - Provide a name (e.g., Weekly Calendar Update).
   - Select Run whether user is logged on or not.
   - Check Run with highest privileges if the repository is saved in a required folder.
4. Configure the Trigger:
   - Go to the Triggers tab and click New.
   - Choose Weekly and select the desired day(s) and time.
5. Configure the Action:
   - Go to the Actions tab and click New.
   - Choose Start a Program.
   - In the Program/script field, browse to your .bat file.
6. Configure the Settings
   - Select Run task as soon as possible after a scheduled start is missed
7. Save and Test:
   - Click OK, enter your credentials (if prompted), and save the task.
   - Find the task in Task Scheduler Library folder.
   - Right-click the task and select Run to test it.
   - Go to the repository and check `script.log` for output.
