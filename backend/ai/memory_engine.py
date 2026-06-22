class MemoryEngine:
    def __init__(self):
        # In a real app, use Redis or a database (SQLite/PostgreSQL)
        # Using a simple dict for local session history
        self.history = {}

    def add_to_history(self, session_id, user_message, ai_response):
        if session_id not in self.history:
            self.history[session_id] = []
        self.history[session_id].append({"user": user_message, "ai": ai_response})
        # Keep only last 10 interactions to save memory
        if len(self.history[session_id]) > 10:
            self.history[session_id].pop(0)

    def get_history(self, session_id):
        return self.history.get(session_id, [])
