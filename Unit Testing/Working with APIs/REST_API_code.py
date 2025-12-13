# using RESTful APIs in Python

import requests
api_url = "http://jsonplaceholder.typicode.com/todos/1"         # jsonplaceholder - free service, provides fake API endpoints that send back responses that requests can process.
response = requests.get(api_url)
response.json()
print(response.json())

# using Put

import requests
url = "http://jsonplaceholder.typicode.com/todos/10"
response = requests.get(url)
response.json()

todo = {'userId':1, 'id':10, 'title':'xxxyyyzzz', 'completed':True}
response = requests.put(url,json=todo)                  # put() - to replace an existing resource with an updated version. This method works by replacing the entire resource 
response.json()                                         # post() - The POST method is used to create new resources. For instance, if the manager of an e-commerce store wanted to add a new product to the database, they would send a POST request to the /products endpoint
                                                        # https://blog.postman.com/what-are-http-methods/ 

print(response.status_code)
print("Data successfully posted ")

print("After put  : ")                                  # You will not see new data as it's fake endpoints
response = requests.get(url)
print(response.json())

# using PATCH                                       # The PATCH method is used to update an existing resource. It is similar to PUT, except that PATCH enables clients to update specific properties on a resource—without overwriting the others.

import requests 
url = "http://jsonplaceholder.typicode.com/todos/10"
todo = {"title":"Maw Lawn"}
response = requests.patch(url,json=todo)                # patch() - Update/Modify 
print("After patch() : ")
print(response.json())
print(response.status_code)

response = requests.get(url)
print(response.json())

# using DELETE

import requests

url = "http://jsonplaceholder.typicode.com/todos/10"
response = requests.delete(url)
response.json()
print(response.status_code)
print(response.json())

