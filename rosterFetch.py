import requests
from bs4 import BeautifulSoup
import json

# URL of the login page
login_url = "https://rmhrosterweb.ssg.org.au/RosterOnProd/Mobile/Account/Login"

# User credentials
with open("credentials.json", "r") as cred_file:
    credentials = json.load(cred_file)

# Start a session
session = requests.Session()

# Get the login page to retrieve any necessary tokens or cookies
login_page = session.get(login_url)
soup = BeautifulSoup(login_page.text, "html.parser")

# If there are CSRF tokens or other hidden fields, extract them here
csrf_token = soup.find("input", {"name": "__RequestVerificationToken"})
if csrf_token:
    credentials["__RequestVerificationToken"] = csrf_token["value"]

# Send the POST request to log in
response = session.post(login_url, data=credentials)

# Check the response
if response.status_code == 200:
    print("Login successful!")
    
    # Navigate to the roster page
    roster_url = "https://rmhrosterweb.ssg.org.au/RosterOnProd/Mobile/Roster/List?pageNo=1&row=1"
    roster_response = session.get(roster_url)

    if roster_response.status_code == 200:
        print("Successfully accessed the roster page!")
        roster_page = BeautifulSoup(roster_response.text, "html.parser")

        # Save the roster HTML to a file for review
        with open("source.html", "w", encoding="utf-8") as file:
            file.write(roster_page.prettify())

        print("Roster saved to source.html")
    else:
        print(f"Failed to access roster page. Status code: {roster_response.status_code}")
else:
    print("Login failed. Check your credentials or the login process.")

