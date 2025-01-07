# RosterOnExport
Export RMH roster-on to .ics calendar files

## Prerequisites
Before using the script, ensure you have the following:

1. **Python 3.7 or later**
   - [Download Python](https://www.python.org/downloads/)
2. **Required Python Libraries**
   - `beautifulsoup4`
   - `ics`

   Install them using pip:
   ```bash
   pip install beautifulsoup4 ics pytz
   ```

## Setup roster2ics.py

### Step 1: Clone or Download the Script
Download the roster2ics.py to a designated folder in your computer OR clone the repository:
```bash
git clone https://github.com/zhongyuex/RosterOnExport.git
cd RosterOnExport
```

### Step 2: Get your roster from RosterOn
Use a browser to view your roster in RosterOn. At the page where you can view your roster, right-click and choose "Save as" to save it as `source.html` in the same folder as your `roster2ics.py` script.

For advanced users, this step can also be automated using `rosterFetch.py` along with a JSON file containing your credentials.

### Step 3: Run the Script
Run the script to log in and export your roster:
```bash
python roster2ics.py
```

### Step 4: View the Output
After the script runs successfully, two files will be generated:
1. `roster.json` - A copy of the fetched roster data for further data processing.
2. `roster.ics` - An iCalendar file ready for import into your calendar application.

## Apple Calendar Desktop App
1. Open Apple Calendar on your Mac.
2. From the menu bar, click File > Import.
3. Browse to the .ics file and click Import.
4. Select the calendar where you want to add the events or create a new calendar.
5. Click OK to complete the import.

## Outlook App
1. Open Outlook on the Web.
2. Click on the Calendar icon in the left-hand navigation bar.
3. In the toolbar, click on Add calendar.
4. Select Upload from file.
5. Click Browse and locate the .ics file on your computer.
6. Choose the calendar you want to import the events into or create a new calendar.
7. Click Import to upload the .ics file.

## Google Calendar on the Web
1. Open Google Calendar.
2. Click the gear icon and select "Settings".
3. It is recommended that you first create a new calendar and add the roster there. That way if there was an issue with the roster you added, you can delete that calendar straightaway without
 affecting your original calendar.
4. Go to "Import & Export".
5. Upload the `roster.ics` file.
