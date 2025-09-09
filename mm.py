import requests

url = "https://50a50cc6-0749-4e02-89b1-5265646fb5ce-00-1xpm17d5ty1us.pike.replit.dev/api/music"

payload = {
    "lyrics": "love+is+pain",
    "tags": "pop+epic ",
    "api_key": "0DlMAcJjxNNJfcABRMGNzmkjxxMdIb_Z8bPVH3sJ-Jo"
}

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())