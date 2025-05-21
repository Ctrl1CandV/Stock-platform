from .models import Agent
import json

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(['GET'])
def dialogueLocalModel(request):
    ''' 使用Ollama与本地模型对话 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'response_content': None,
        'thinking_content': None 
    }
    try:
        user_id = int(request.GET.get('userID'))
        user_content = request.GET.get('userContent')
        agent = Agent(user_id)
        response_content, thinking_content = agent.send_message(user_content)
        agent.close()
        response['status'] = 'SUCCESS'
        response['response_content'], response['thinking_content'] = response_content, thinking_content
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)