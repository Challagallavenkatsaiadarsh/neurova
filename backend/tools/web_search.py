# =========================================
# FILE: backend/tools/web_search.py (LEVEL 8)
# =========================================

from duckduckgo_search import DDGS


class WebSearchEngine:

    def __init__(self):
        print("🌐 WebSearch Engine Initialized")

    # =========================================
    # MAIN SEARCH FUNCTION
    # =========================================
    def search(self, query: str, max_results: int = 5):

        if not query:
            return []

        results = []

        try:
            with DDGS() as ddgs:

                for r in ddgs.text(query, max_results=max_results):

                    results.append({
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })

            return results

        except Exception as e:
            print("WebSearch Error:", str(e))
            return []


# =========================================
# SIMPLE FUNCTION WRAPPER (USED BY ROUTER)
# =========================================
def search_web(query: str):

    engine = WebSearchEngine()
    results = engine.search(query)

    # =========================================
    # FORMAT FOR AI ROUTER
    # =========================================
    formatted = []

    for r in results:

        title = r.get("title", "No title")
        link = r.get("link", "")
        snippet = r.get("snippet", "")

        formatted.append(
            f"🔹 {title}\n{snippet}\n🔗 {link}"
        )

    return formatted if formatted else ["No results found."]
