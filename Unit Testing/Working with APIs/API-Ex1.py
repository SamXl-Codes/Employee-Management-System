# Working with API 
# Sign up with openweathermap api to get the API key, it will get activated in 2 hours,
# You will receive an email specifying the API key and the API endpoints

import requests
import datetime as dt 
import json

base_url = "http://api.openweathermap.org/data/2.5/weather?"

API_key = open('key1.txt','r').read()           # API key is stored in key1.txt, to keep it hidden from the source code / not to show in the video
city = "Dublin"

print(API_key)

url = base_url + "q=" + city + "&APPID="+API_key

response = requests.get(url)
res = response.json()
print(res)

res_text = json.dumps(res, indent=4)
print(res_text)

