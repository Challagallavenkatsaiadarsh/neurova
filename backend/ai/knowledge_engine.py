import json
import os
import difflib # Added for fuzzy matching

class KnowledgeEngine:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "..", "data")

    def get_info(self, topic, key):
        file_path = os.path.join(self.data_path, f"{topic}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. Normalize key (case-insensitive)
            normalized_key = key.lower().strip()
            
            # 2. Direct Match
            if normalized_key in data:
                return self._format_response(data[normalized_key])
            
            # 3. Fuzzy Match (Find similar keys if exact match fails)
            # This helps when the user types "Prabhas" but data has "prabhas"
            matches = difflib.get_close_matches(normalized_key, data.keys(), n=1, cutoff=0.6)
            if matches:
                return self._format_response(data[matches[0]])
                
            return None # Return None to trigger Web Search fallback in your Router

        except Exception as e:
            return f"Error accessing database: {str(e)}"

    def _format_response(self, content):
        """Helper to convert JSON objects into readable strings."""
        if isinstance(content, dict):
            # If it's a dict (like movie data), turn it into a clean list
            return "\n".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in content.items()])
        return str(content)
