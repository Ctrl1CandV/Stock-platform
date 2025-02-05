from .models import user_accounts, stock_ownership, stock_transactions
from email_validator import validate_email, EmailNotValidError
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db import transaction
import json

'''
用户模块功能：
1. 注册、登录和个人信息补充
2. 账号名、密码和余额更改
3. 股票持仓查询
4. 证券交易记录查询
'''

@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    ''' 用户注册 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_email = body.get('userEmail')
        user_name = body.get('userName')
        user_password = body.get('userPassword')

        with transaction.atomic():
            if user_accounts.objects.filter(user_email=user_email).exists():
                response['errorMessage'] = "邮箱已注册"
                return JsonResponse(response, status=400)

            # 验证邮箱，创建用户
            validate_email(user_email)
            user = user_accounts(
                user_email=user_email,
                user_name=user_name
            )
            user.setPassword(user_password)
            user.save()

        response['status'] = 'SUCCESS'

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except EmailNotValidError as e:
        response['errorMessage'] = f"邮箱格式错误: {str(e)}"
        return JsonResponse(response, status=400)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)


@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    ''' 用户登录 '''

    response = {
        'status': 'ERROR',
        'user': None,
        'errorMessage': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_email = body.get('userAccount')
        user_password =body.get('password')

        user = user_accounts.objects.get(user_email=user_email)
        if user.checkPassword(user_password):
            response['status'], response['user'] = 'SUCCESS', model_to_dict(user)
        else:
            response['errorMessage'] = "密码错误"
            return JsonResponse(response, status=401)

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
def gainUserInformation(request):
    ''' 获取用户个人信息 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'user': None
    }
    try:
        user_id = request.GET.get('userID')
        user = user_accounts.objects.get(user_id=user_id)
        response['status'], response['user'] = 'SUCCESS', model_to_dict(user, exclude=['user_password'])
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
def updateProfile(request):
    ''' 补充用户个人信息 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_data = body.get('userData')
        user_id = body.get('userID')

        with transaction.atomic():
            user = user_accounts.objects.get(user_id=user_id)

            # 当键名等于属性名时，将键对应值赋予属性
            for field, value in user_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            user.save()

            response['status'] = 'SUCCESS'
            response['userID'] = user_id

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
def updateBalance(request):
    ''' 更新用户余额 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        new_balance = body.get('newBalance')

        with transaction.atomic():
            user = user_accounts.objects.get(user_id=user_id)
            user.user_balance = new_balance
            user.save()
            response['status'], response['userID'] = 'SUCCESS', user_id

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
def changePassword(request):
    ''' 修改用户密码 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        old_password = body.get('oldPassword')
        new_password = body.get('newPassword')

        with transaction.atomic():
            user = user_accounts.objects.get(user_id=user_id)
            if user.checkPassword(old_password):
                user.setPassword(new_password)
                user.save()

                response['status'] = 'SUCCESS'
                response['userID'] = user.user_id
            else:
                response['errorMessage'] = "旧密码错误"
                return JsonResponse(response, status=401)

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

# 用户股票模块的功能
@csrf_exempt
@require_http_methods(['GET'])
def getStockOwnership(request):
    ''' 查询用户股票持仓 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'stockOwnershipList': None
    }
    try:
        user_id = request.GET.get('userID')
        stock_ownerships = stock_ownership.objects.filter(user_id=user_id)

        stock_ownership_list = []
        for ownership in stock_ownerships:
            stock_ownership_map = model_to_dict(ownership, fields=['stock_code', 'stock_name', 'hold_nunmber', 'purchase_per_price'])
            stock_ownership_list.append(stock_ownership_map)

        response['status'], response['stockOwnershipList'] = "SUCCESS", stock_ownership_list

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
def getTransactionRecords(request):
    ''' 查询用户交易记录 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'stockTransactionList': None
    }
    try:
        user_id = request.GET.get('userID')
        user_transactions = stock_transactions.objects.filter(user_id=user_id)

        stock_transaction_list = []
        for user_transaction in user_transactions:
            stock_transaction_map = model_to_dict(
                user_transaction,
                fields=['transaction_type', 'stock_code', 'stock_name', 'transaction_number', 'per_price', 'gains']
            )
            stock_transaction_list.append(stock_transaction_map)
        response['status'], response['stockTransactionList'] = "SUCCESS", stock_transaction_list

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