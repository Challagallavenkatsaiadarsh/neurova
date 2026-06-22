from ai.topic_classifier import TopicClassifier
from ai.knowledge_engine import KnowledgeEngine
from ai.web_search import WebSearchEngine
from ai.response_generator import ResponseGenerator

# Initialize engines as classes
classifier = TopicClassifier()
knowledge_engine = KnowledgeEngine()
web_search_engine = WebSearchEngine()
generator = ResponseGenerator()

def refine_query(message, topic):
    """Refine user input to get better results from the web."""
    if topic == "movies": # Ensure this matches your classifier's key
        return f"official box office collection and release details of the Telugu movie '{message}'"
    elif topic == "science":
        return f"scientific definition and explanation of '{message}'"
    return message

def route_message(data: dict):
    # Extract message safely
    message = data.get("message", "")
    if not message:
        return {"success": False, "error": "No message provided"}

    # 1. Detect Topic
    topic = classifier.detect_topic(message)
    
    print(f"\n--- DEBUG START ---")
    print(f"Message: {message} | Detected Topic: {topic}")

    # 2. Try Local Knowledge (JSON)
    # Pass the topic to identify which .json file to open
    answer = knowledge_engine.get_info(topic, message)
    
    if answer:
        print(f"SOURCE: Found in Local JSON ({topic}.json)")
    else:
        # 3. Fallback to Web Search
        print(f"SOURCE: Triggering Web Search")
        refined_query = refine_query(message, topic)
        answer = web_search_engine.search(refined_query)
        print(f"WEB RESULT: {answer[:100]}...")
    
    # 4. Generate Grok-style response
    final_response = generator.generate(answer, style="grok")
    print(f"--- DEBUG END ---\n")
    
    return {
        "success": True,
        "type": "text",
        "response": final_response,
        "topic": topic,
        "alerts": [],
        "cyber_score": 100
    }
