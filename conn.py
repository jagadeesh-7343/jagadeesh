import requests 

result = requests.get("http://127.0.0.1:5000/ai-sugges")

print(result.text)
print(result)
print(result.status_code)