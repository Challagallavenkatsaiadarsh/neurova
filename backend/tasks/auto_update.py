import time
import requests

API = "http://127.0.0.1:5000/search"

# =========================
# AUTO UPDATE LOOP
# =========================
def run_updates():
    while True:
        try:
            r = requests.get(API, params={"q": "news"})
            print("Auto update check:", r.status_code)
        except Exception as e:
            print("Update error:", e)

        time.sleep(60)  # every 1 minute


if __name__ == "__main__":
    run_updates()
