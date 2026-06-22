import requests

API_KEY = "AIzaSyAa8NCPQY1rVIg6hllQHwO0BgqA7npBOWI"


def check_url_safety(url: str):
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"

    payload = {
        "client": {
            "clientId": "neurova",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=10)
        data = res.json()

        # If "matches" exists → dangerous
        if "matches" in data:
            return {
                "safe": False,
                "threats": data["matches"]
            }

        return {
            "safe": True,
            "threats": []
        }

    except Exception as e:
        return {
            "safe": True,   # fail-safe (DO NOT block websites)
            "threats": [],
            "error": str(e)
        }
