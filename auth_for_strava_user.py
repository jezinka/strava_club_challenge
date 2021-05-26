import json

import requests

from const import TOKEN_JSON, STRAVA_OAUTH_TOKEN_URL, GRANT_TYPE_AUTHORIZATION_CODE, CLIENT_ID, CLIENT_SECRET, CODE

# Make Strava auth API call with your
# client_code, client_secret and code

# https://www.strava.com/oauth/authorize?client_id=[ClientID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

response = requests.post(
    url=STRAVA_OAUTH_TOKEN_URL,
    data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': CODE,
        'grant_type': GRANT_TYPE_AUTHORIZATION_CODE
    }
)

# Save json response as a variable
strava_tokens = response.json()
# Save tokens to file
with open(TOKEN_JSON, 'w') as outfile:
    json.dump(strava_tokens, outfile)

print(outfile)
# Open JSON file and print the file contents 
# to check it's worked properly
with open(TOKEN_JSON) as check:
    data = json.load(check)
print(data)
