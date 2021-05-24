# code built off script from the following blog post
# https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86

import json
import time
from datetime import datetime

import gspread
import requests
from dotenv import dotenv_values

from activity import Activity


# connect to google spreadsheet
# input
# key: key to google sheet
# worksheet: name of worksheet
# output
# sheet: google sheet object

def connect_to_spreadsheet(key, worksheet):
    # connect to google sheet
    google_spread_oauth = gspread.oauth()

    # open spreadsheet
    sheet = google_spread_oauth.open_by_key(key).worksheet(worksheet)
    return sheet


# get first date of challenge
# input
# sheet: google sheet
# output
# start_date: last date in spreadsheet
def get_last_date(sheet):
    last_date_cell_value = list(filter(None, sheet.col_values(1)))[-1]
    last_date = datetime.strptime(last_date_cell_value, "%Y-%m-%d").date()

    return last_date


# convert date to epoch time
def convert_to_epoch(input_date):
    return (datetime(input_date.year, input_date.month, input_date.day).timestamp())


# call strava api to get user activities
# input
# start_date_epoch: timestamp of date (at midnight) when the challenge starts
# client_id : client id of strava application
# client_secret : secret key of strava application
# output
# activities: list of activities from strava
def get_user_activities_from_strava(start_date_epoch, client_id, client_secret):
    # create list of user activities
    activities = []

    ## Get the tokens from file to connect to Strava
    with open('strava_token.json') as json_file:
        strava_tokens = json.load(json_file)
    ## If access_token has expired then use the refresh_token to get the new access_token
    if strava_tokens['expires_at'] < time.time():
        strava_tokens = refresh_strava_token(client_id, client_secret, strava_tokens['refresh_token'])

    # Loop through all activities
    page = 1
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens['access_token']

    while page < 2:  # this is to limit the results coming back just in case a user has hundreds of activities in that window

        # get page of activities from Strava
        r = requests.get(
            url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page) + '&after=' + str(
                start_date_epoch))
        r = r.json()

        # if no results then exit loop
        if not r:
            break

        for x in range(len(r)):
            if r[x]['type'] == 'InlineSkate':
                activity = Activity(r[x]['start_date_local'], r[x]['distance'])
                activities.append(activity)

        # increment page
        page += 1

    return activities


def refresh_strava_token(client_id, client_secret, refresh_token):
    # Make Strava auth API call with current refresh token
    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    # Save response as json in new variable
    new_strava_tokens = response.json()
    # Save new tokens to file
    with open('strava_token.json', 'w') as outfile:
        json.dump(new_strava_tokens, outfile)
    # Use new Strava tokens from now
    return new_strava_tokens


# write weekly user data to google sheet
# input
# sheet: google sheet where user information is stored
# activites: list of all activites
def write_to_sheet(sheet, activites):
    row_index = get_first_empty_row(sheet)
    for a in activites:
        sheet.update_cell(row_index, 1, a.start_date)
        sheet.update_cell(row_index, 2, a.distance)
        row_index += 1


def get_first_empty_row(sheet):
    values = sheet.col_values(1)
    return len(values) + 1


def main():
    # CONFIG
    config = dotenv_values(".env")

    client_id = int(config['CLIENT_ID'])
    client_secret = config['CLIENT_SECRET']
    google_sheet_key = config['GOOGLE_SHEET_KEY']
    google_sheet_name = config['GOOGLE_SHEET_NAME']

    # connect to google sheet
    sheet = connect_to_spreadsheet(google_sheet_key, google_sheet_name)

    # get last date from spreadSheet
    start_date = get_last_date(sheet)
    day_after = datetime(start_date.year, start_date.month, start_date.day + 1)
    start_date_epoch = convert_to_epoch(day_after)

    # get user activity from strava
    activities = get_user_activities_from_strava(start_date_epoch, client_id, client_secret)

    # update google sheet with challenge values
    write_to_sheet(sheet, activities)


if __name__ == "__main__":
    main()
