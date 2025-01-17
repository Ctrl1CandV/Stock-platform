from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from .models import user_accounts
import json

'''
管理员仅有三个针对用户的基础功能
POST会改变数据，GET不会
'''

@csrf_exempt
@require_http_methods(['POST'])
def deleteUser(request):
    ''' 伪删除用户账户 '''

    response = {
        'status': 'ERROR',
        'userID': None,
        'errorMessage': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        response['userID'] = user_id

        with transaction.atomic():
            user = user_accounts.objects.get(id=user_id)
            user.status = False
            user.save()
            response['status'] = "SUCCESS'"

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response, status=404)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['POST'])
def editUserBalance(request):
    ''' 更改用户的余额 '''

    response = {
        'status': 'ERROR',
        'userID': None,
        'errorMessage': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        new_balance = body.get('newBalance')
        response['userID'] = user_id

        with transaction.atomic():
            user = user_accounts.objects.get(id=user_id)
            if user.status:
                user.balance = new_balance
                user.save()
                response['status'] = "SUCCESS"
            else:
                response['errorMessage'] = "用户账号已弃用"
                return JsonResponse(response, status=403)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response, status=404)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def queryUsers(request):
    ''' 查询用户账户 '''

    response = {
        'status': 'ERROR',
        'userList': None,
        'errorMessage': None
    }
    try:
        users = user_accounts.objects.all()
        user_list = []
        for user in users:
            user_map = {
                'userId': user.user_id,
                'userEmail': user.user_email,
                'userName': user.user_name,
                'userBalance': user.user_balance,
                'status': user.status
            }
            user_list.append(user_map)
        response['userList'], response['status'] = user_list, "SUCCESS"
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)