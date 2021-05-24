import json

import requests
from dotenv import dotenv_values

# Make Strava auth API call with your
# client_code, client_secret and code

# https://www.strava.com/oauth/authorize?client_id=[ClientID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

config = dotenv_values(".env")

client_id = int(config['CLIENT_ID'])
client_secret = config['CLIENT_SECRET']
code = config['CODE']


response = requests.post(
                    url = 'https://www.strava.com/oauth/token',
                    data = {
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'code': code,
                            'grant_type': 'authorization_code'
                            }
                )

#Save json response as a variable
strava_tokens = response.json()
# Save tokens to file
with open('strava_token.json', 'w') as outfile:
    json.dump(strava_tokens, outfile)

print(outfile)
# Open JSON file and print the file contents 
# to check it's worked properly
with open('strava_token.json') as check:
  data = json.load(check)
print(data)

