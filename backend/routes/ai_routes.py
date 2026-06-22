from flask import Blueprint, request, jsonify
from backend.ai.topic_classifier import TopicClassifier
from backend.ai.knowledge_engine import KnowledgeEngine
from backend.ai.web_search import WebSearchEngine

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('message')
    topic = TopicClassifier().classify(user_query)
    
    # 1. Try local data
    engine = KnowledgeEngine()
    fact = engine.get_info(topic, user_query)
    
    # 2. If not found, use Web Search
    if not fact:
        fact = WebSearchEngine().search(user_query)
        
    return jsonify({"response": fact})
