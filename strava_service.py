import json
import time

import requests

from activity import Activity
from const import GRANT_TYPE_REFRESH_TOKEN, INLINE_SKATE, STRAVA_OAUTH_TOKEN_URL, STRAVA_API_URL, TOKEN_JSON, \
    CLIENT_SECRET, CLIENT_ID


def refresh_strava_token(refresh_token):
    # Make Strava auth API call with current refresh token
    response = requests.post(
        url=STRAVA_OAUTH_TOKEN_URL,
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': GRANT_TYPE_REFRESH_TOKEN,
            'refresh_token': refresh_token
        }
    )
    # Save response as json in new variable
    new_strava_tokens = response.json()
    # Save new tokens to file
    with open(TOKEN_JSON, 'w') as outfile:
        json.dump(new_strava_tokens, outfile)
    # Use new Strava tokens from now
    return new_strava_tokens


# call strava api to get user activities
# input
# start_date_epoch: timestamp of date (at midnight) when the challenge starts
# end_date_epoch: timestamp of date (at midnight) when the year ends
# client_id : client id of strava application
# client_secret : secret key of strava application
# output
# activities: list of activities from strava
def get_user_activities_from_strava(start_date_epoch, end_date_epoch):
    # create list of user activities
    activities = []

    ## Get the tokens from file to connect to Strava
    with open(TOKEN_JSON) as json_file:
        strava_tokens = json.load(json_file)
    ## If access_token has expired then use the refresh_token to get the new access_token
    if strava_tokens['expires_at'] < time.time():
        strava_tokens = refresh_strava_token(strava_tokens['refresh_token'])

    # Loop through all activities
    page = 1
    access_token = strava_tokens['access_token']

    while page < 2:  # this is to limit the results coming back just in case a user has hundreds of activities in that window

        # get page of activities from Strava
        r = requests.get(
            STRAVA_API_URL + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page) + '&after=' + str(
                start_date_epoch) + '&before=' + str(end_date_epoch))
        r = r.json()

        # if no results then exit loop
        if not r:
            break

        for x in range(len(r)):
            if r[x]['type'] == INLINE_SKATE:
                activity = Activity(r[x]['start_date_local'], r[x]['distance'])
                activities.append(activity)

        # increment page
        page += 1

    return sorted(activities, key=lambda a: a.training_date)
