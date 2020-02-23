from __future__ import print_function

import os.path
import pickle

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils import ACTION_MAKE, ACTION_DELETE

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

BUCHAREST_TIMEZONE = 'Europe/Bucharest'
dateFormat = "YYYY-MM-DDTHH:MM:SS"

# As Friday of the first week of the semester
startSemesterDay = "2020-02-24"

# As Friday of the last week of the semester
endSemester = "2020-05-22"

# Start of vacation as MONDAY of the first week of vacation
startVacation = "2020-04-20"

# End of vacation as SUNDAY of the LAST week of vacation
endVacation = "2020-04-26"

SEMINARY_COLOR = '2'
LABORATORY_COLOR = '5'
COURSE_COLOR = '4'

RRULE_EVERY_OTHER_WEEK = 'RRULE:FREQ=DAILY;INTERVAL=14;UNTIL=YYYYMMDDTHHMMSS'
RRULE_EVERY_WEEK = 'RRULE:FREQ=DAILY;INTERVAL=14;UNTIL=YYYYMMDDTHHMMSS'


def makeCalendarEntries(entriesRaw, action):
    creds = None
    eventsCreated = []

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    if (action == ACTION_MAKE):
        for entryRaw in entriesRaw:
            startVacationSunday = pd.to_datetime(startVacation) + pd.DateOffset(days=-1)
            startVacationSunday = str(startVacationSunday.year) + "-" + str(startVacationSunday.month) + "-" + str(
                startVacationSunday.day)
            endVacationMonday = pd.to_datetime(endVacation) + pd.DateOffset(days=1)
            endVacationMonday = str(endVacationMonday.year) + "-" + str(endVacationMonday.month) + "-" + str(
                endVacationMonday.day)

            event1 = service.events().insert(calendarId='primary',
                                             body=generateEventJson(entryRaw, startSemesterDay, startVacationSunday,
                                                                    1)).execute()
            eventsCreated.append(event1['id'])
            event2 = service.events().insert(calendarId='primary',
                                             body=generateEventJson(entryRaw, endVacationMonday, endSemester,
                                                                    1)).execute()
            eventsCreated.append(event2['id'])
            print('Event1 created: ' + event1.get('htmlLink'))
            print('Event2 created: ' + event2.get('htmlLink'))
        with open("createdEvents.txt", "w") as ids:
            ids.truncate()
            for id in eventsCreated:
                ids.write(id + "\n")
            ids.close()

    elif (action == ACTION_DELETE):
        with open("createdEvents.txt", "r") as ids:
            eventIdList = ids.readlines()
            eventIdList = [x.strip() for x in eventIdList]
        for id in eventIdList:
            page_token = None
            while True:
                events = service.events().instances(calendarId='primary', eventId=id,
                                                    pageToken=page_token).execute()
                for event in events['items']:
                    print("Deleting eventId " + event['id'] + " with title: " + event['summary'])
                    service.events().delete(calendarId='primary', eventId=event['id']).execute()
                page_token = events.get('nextPageToken')
                if not page_token:
                    break


def generateEventStartEndDateTime(eventRaw, startDate, startWeekParity):
    startEventDateTime = ""
    endEventDateTime = ""
    byweeklyOffset = 0

    if (startWeekParity == 1):
        if (eventRaw['Frecventa'] == "sapt. 2"):
            byweeklyOffset = 7
    elif (startWeekParity == 2):
        if (eventRaw['Frecventa'] == "sapt. 1"):
            byweeklyOffset = 7

    hours = eventRaw['Orele'].split("-")
    if (eventRaw['Ziua'] == 'Luni'):
        startEventDateTime = startDate + "T" + hours[0] + ":00:00"
        endEventDateTime = startDate + "T" + hours[1] + ":00:00"
    elif (eventRaw['Ziua'] == 'Marti'):
        startEventDate = pd.to_datetime(startDate) + pd.DateOffset(days=1 + byweeklyOffset)
        startEventDate = str(startEventDate.year) + "-" + str(startEventDate.month) + "-" + str(startEventDate.day)
        startEventDateTime = startEventDate + "T" + hours[0] + ":00:00"
        endEventDateTime = startEventDate + "T" + hours[1] + ":00:00"
    elif (eventRaw['Ziua'] == 'Miercuri'):
        startEventDate = pd.to_datetime(startDate) + pd.DateOffset(days=2 + byweeklyOffset)
        startEventDate = str(startEventDate.year) + "-" + str(startEventDate.month) + "-" + str(startEventDate.day)
        startEventDateTime = startEventDate + "T" + hours[0] + ":00:00"
        endEventDateTime = startEventDate + "T" + hours[1] + ":00:00"
    elif (eventRaw['Ziua'] == 'Joi'):
        startEventDate = pd.to_datetime(startDate) + pd.DateOffset(days=3 + byweeklyOffset)
        startEventDate = str(startEventDate.year) + "-" + str(startEventDate.month) + "-" + str(startEventDate.day)
        startEventDateTime = startEventDate + "T" + hours[0] + ":00:00"
        endEventDateTime = startEventDate + "T" + hours[1] + ":00:00"
    elif (eventRaw['Ziua'] == 'Vineri'):
        startEventDate = pd.to_datetime(startDate) + pd.DateOffset(days=4 + byweeklyOffset)
        startEventDate = str(startEventDate.year) + "-" + str(startEventDate.month) + "-" + str(startEventDate.day)
        startEventDateTime = startEventDate + "T" + hours[0] + ":00:00"
        endEventDateTime = startEventDate + "T" + hours[1] + ":00:00"

    return startEventDateTime, endEventDateTime


def setRecuranceRule(eventRaw, endTime):
    endTimeArray = endTime.split("-")
    for i in range(0, len(endTimeArray)):
        if (int(endTimeArray[i]) < 10):
            endTimeArray[i] = "0" + str(int(endTimeArray[i]))
    endTime = endTimeArray[0] + endTimeArray[1] + endTimeArray[2]
    if (eventRaw['Frecventa'] == ""):
        return "RRULE:FREQ=DAILY;INTERVAL=7;" + "UNTIL=" + endTime + "T235959Z"
    else:
        return "RRULE:FREQ=DAILY;INTERVAL=14;" + "UNTIL=" + endTime + "T235959Z"


def generateEventJson(eventRaw, startDate, endDate, startWeekParity):
    colorId = setColorForEvent(eventRaw)
    startDateTime, endDateTime = generateEventStartEndDateTime(eventRaw, startDate, startWeekParity)
    recuranceRule = setRecuranceRule(eventRaw, endDate)

    eventJson = {
        "end": {
            "timeZone": BUCHAREST_TIMEZONE,
            "dateTime": endDateTime
        },
        "start": {
            "timeZone": BUCHAREST_TIMEZONE,
            "dateTime": startDateTime
        },
        "summary": eventRaw['Disciplina'],
        "description": "Sala: " + eventRaw['Sala'] + "\n" + "Prof: " + eventRaw['Cadrul didactic'],
        "colorId": colorId,
        "recurrence": [
            recuranceRule
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": 60
                }
            ]
        }
    }
    return eventJson


def setColorForEvent(eventRaw):
    colorId = "0"
    if (eventRaw['Tipul'] == 'Curs'):
        colorId = COURSE_COLOR
    elif (eventRaw['Tipul'] == 'Laborator'):
        colorId = LABORATORY_COLOR
    elif (eventRaw['Tipul'] == 'Seminar'):
        colorId = SEMINARY_COLOR
    return colorId
