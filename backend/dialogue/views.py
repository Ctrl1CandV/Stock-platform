from utils.response_view import api_view
from .models import Agent
import json

@api_view(methods=['GET'])
def dialogueLocalModel(request, params):
    ''' 使用Ollama与本地模型对话 '''
    user_id, user_content = int(params.get('userID')), params.get('userContent')
    agent = Agent(user_id)
    response_content, thinking_content = agent.send_message(user_content)
    agent.close()
    return {
        'response_content': response_content,
        'thinking_content': thinking_content
    }