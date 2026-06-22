class TopicClassifier:
    def __init__(self):
        # Map keywords to your JSON filenames
        self.category_map = {
            "movies": ["movie", "box office", "actor", "director", "collection", "film"],
            "space": ["mars", "space", "nasa", "galaxy", "rocket", "planet"],
            "science": ["science", "physics", "chemistry", "biology", "atom"],
            "technology": ["ai", "robot", "tech", "software", "computer", "internet"],
            "cyber_knowledge": ["security", "cyber", "hack", "virus", "password"]
        }

    def detect_topic(self, query):
        query = query.lower()
        for category, keywords in self.category_map.items():
            if any(keyword in query for keyword in keywords):
                return category
        return "general"
