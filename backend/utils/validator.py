from jwt import ExpiredSignatureError, DecodeError
from functools import wraps
import jwt

from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from .logger import Logger

# 用户的Token校验装饰器
def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = {
            'status': 'ERROR',
            'errorMessage': None
        }
        logger = Logger()
        try:
            # 从请求头中获取Token
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')
            if len(token) < 2 or token[0] != 'Bearer':
                response['errorMessage'] = "无效的Token格式"
                return JsonResponse(response)

            # 解析Token
            payload = jwt.decode(
                token[1],
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            cache_key = f'user_{user_id}_token'
            cache_result = cache.get(cache_key)
            if cache_result != token[1]:
                logger.warning(f"非法请求:使用失效Token,user_id:{user_id},IP:{request.META.get('REMOTE_ADDR')}")
                response['errorMessage'] = "无效Token"
                return JsonResponse(response)
        except AttributeError:
            logger.warning(f"非法请求:未携带有效Token,IP:{request.META.get('REMOTE_ADDR')}")
            response['errorMessage'] = "未携带Token信息"
            return JsonResponse(response)
        except ExpiredSignatureError as e:
            response['errorMessage'] = "Token已过期"
            return JsonResponse(response)
        except Exception as e:
            response['errorMessage'] = str(e)
            return JsonResponse(response)
        
        return view_func(request, *args, **kwargs)
    return wrapper