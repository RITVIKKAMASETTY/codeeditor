import requests
response = requests.get("http://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q=London")
print(response.json())
