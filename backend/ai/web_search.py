import os
from tavily import TavilyClient

class WebSearchEngine:
    def __init__(self):
        # Always use environment variables for API keys
        self.api_key = os.getenv("TAVILY_API_KEY", "your_api_key_here")
        self.client = TavilyClient(api_key=self.api_key)

    def search(self, query):
        try:
            # 'advanced' search depth gives better accuracy for complex facts
            # 'include_answer=True' tells Tavily to generate a quick summary for you
            response = self.client.search(
                query=query, 
                search_depth="advanced", 
                max_results=3,
                include_answer=True
            )
            
            # Return the LLM-generated answer if available, 
            # otherwise combine snippets from the results
            if response.get('answer'):
                return response['answer']
            
            results = response.get('results', [])
            return "\n\n".join([f"{r['title']}: {r['content']}" for r in results])
            
        except Exception as e:
            return f"Search service currently unavailable: {str(e)}"
