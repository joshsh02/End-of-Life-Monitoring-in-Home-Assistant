import requests

products = requests.get("https://endoflife.date/api/all.json").json()

for product in products[:10]:
    response = requests.get(f"https://endoflife.date/api/{product}.json").json()

    for entry in response:
        print(f"{product} EOL dates: {entry['cycle']}: {entry['eol']}")
