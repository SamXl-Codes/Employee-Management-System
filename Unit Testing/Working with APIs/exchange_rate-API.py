#Extract value from the JSON response using the API 
#
# API Key is available at: key3.txt  

import urllib.parse
import requests

# website: https://www.exchangerate-api.com/


baseUrl = open('key3.txt','r').read()                               # Keep your keys safe and secure. Handle them with environmental variables and secrets 
                                                                    # https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure
try:
    ans = 'y'
    while (ans != 'n'):
        val1 = input('\nEnter first Currency value (e.g. EUR): ')
        val2 = input('Enter second currency value (e.g. USD): ')
        val = val1+"/"+val2

        url = baseUrl+val

        json_data = requests.get(url).json()
        result = json_data['conversion_rate']

        print("Conversion rate from "+val1+" to "+val2+" = ",result)
        print("1",val1,'=',result,val2)
        ans = input('Continue? ')
        
except Exception as e:
    print("Run time error...")
    print(e)    