from typing import Any, List, Dict, Optional, Callable
from jwt import ExpiredSignatureError, DecodeError
from functools import wraps
import jwt, json

from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from .logger import logger

class APIResponse:
    """ 统一的API响应类 """
    def __init__(self, status: str = 'ERROR', error_message: str = None, **kwargs):
        self.data = {
            'status': status,
            'errorMessgae': error_message,
            **kwargs
        }
    
    def to_json(self) -> JsonResponse:
        return JsonResponse(self.data)

class RequestHandler:
    """ 统一的请求处理器 """
    @staticmethod
    def get_params(request, method: str) -> Dict[str, Any]:
        if method == 'GET':
            return dict(request.GET.items())
        elif method == 'POST':
            try:
                return json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError("无效的JSON负载")
        else:
            raise ValueError(f"不支持的请求方法: {method}")

class CacheManager():
    """ 缓存管理器 """
    @staticmethod
    def cache_proxy(cache_key: str, function: Callable, timeout: int) -> JsonResponse:
        cache_result = cache.get(cache_key)
        if cache_result is not None:
            return cache_result
        response = function()
        if hasattr(response, 'content'):
            data = json.loads(response.content)
            if data.get('status') == "SUCCESS":
                cache_data = {
                    key: value for key, value in data.items()
                    if key not in ('status', 'errorMessage')
                }
                cache.set(cache_key, cache_data, timeout)
        return response

class TokenValidator:
    """ Token校验器 """
    @staticmethod
    def validate(request) -> str:
        try:
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')
            if len(token) < 2 or token[0] != 'Bearer':
                return "无效的Token格式"
            payload = jwt.decode(token[1], settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            cache_key = f'user_{user_id}_token'
            cache_result = cache.get(cache_key)
            if cache_result != token[1]:
                logger.warning(f"非法请求:使用失效Token,user_id:{user_id},IP:{request.META.get('REMOTE_ADDR')}")
                return "无效Token"
        except AttributeError:
            logger.warning(f"非法请求:未携带有效Token,IP:{request.META.get('REMOTE_ADDR')}")
            return "未携带Token信息"
        except ExpiredSignatureError:
            return "Token已过期,请重新登录"
        except Exception as e:
            return str(e)
        return None

def api_view(methods: List[str], use_cache: bool = False, cache_timeout: int = 60 * 60 * 24, require_token: bool = True):
    """ API视图封装器 """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if methods and request.method not in methods:
                return APIResponse(error_message=f"不支持的请求方法: {request.method}").to_json()
            if require_token:
                message = TokenValidator.validate(request)
                if message:
                    return APIResponse(error_message=message).to_json()
            
            try:
                params = RequestHandler.get_params(request, request.method)

                if use_cache:
                    cache_key = func.__name__ + '_' + '_'.join([str(value) for value in params.values()])
                    def view_function():
                        return func(request, params, *args, **kwargs)
                    result = CacheManager.cache_proxy(cache_key, view_function, cache_timeout)
                else:
                    result = func(request, params, *args, **kwargs)

                if isinstance(result, APIResponse):
                    return result.to_json()
                elif isinstance(result, dict):
                    return APIResponse(status="SUCCESS", **result).to_json()
                elif isinstance(result, JsonResponse):
                    return result
                else:
                    return APIResponse(error_message="无效的响应类型").to_json()
            except ValueError as e:
                return APIResponse(error_message=str(e)).to_json()
            except json.JSONDecodeError:
                return APIResponse(error_message="无效的JSON负载").to_json()
            except Exception as e:
                return APIResponse(error_message=str(e)).to_json()
        
        return wrapper
    return decorator