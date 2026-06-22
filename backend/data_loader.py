import os
import pandas as pd

# =========================
# FIXED BASE PATH
# =========================
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# =========================
# LOAD DATASET FILE
# =========================
def load_csv(folder, file):
    path = os.path.join(BASE_DIR, folder, file)

    if not os.path.exists(path):
        print(f"[DATA ERROR] Missing file: {path}")
        return []

    try:
        df = pd.read_csv(path).fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[CSV ERROR] {file}: {e}")
        return []


# =========================
# GET DATASET
# =========================
def get_dataset(name):
    datasets = {
        "animals": load_csv("animals", "animals.csv"),
        "games": load_csv("games", "games.csv"),
        "sports": load_csv("sports", "sports.csv"),
        "movies": load_csv("movies", "movies.csv"),
        "politics": load_csv("politics", "politics.csv"),
        "news": load_csv("news", "news.csv"),
    }
    return datasets.get(name, [])


# =========================
# SMART SEARCH ENGINE (UPGRADED)
# =========================
def search_all(query):
    query = query.lower().strip()
    results = []

    if not query:
        return []

    for name in ["animals", "games", "sports", "movies", "politics", "news"]:
        data = get_dataset(name)

        for item in data:
            # smarter matching (only values, not full dict string)
            if any(query in str(v).lower() for v in item.values()):
                results.append({
                    "category": name,
                    "data": item
                })

    return results
