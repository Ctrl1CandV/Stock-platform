from .models import user_accounts, stock_ownership, stock_transactions, user_favorite_stocks, stock_basic
from email_validator import validate_email, EmailNotValidError
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, StreamingHttpResponse
from platform_functions.tushare_client import ts, pro
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.db import transaction
from django.utils import timezone
import os, re, json, requests

'''
用户模块功能：
1. 注册、登录和个人信息补充
2. 账号名、密码和余额更改
3. 股票持仓查询
4. 证券交易记录查询
'''

def validatePasswordComplexity(user_password: str):
    if len(user_password) < 8 or len(user_password) > 15:
        raise Exception("密码长度必须在8-15位之间")

    if not any(char.isdigit() for char in user_password):
        raise Exception("密码必须包含至少一个数字")
    
    if not any(char.isalpha() for char in user_password):
        raise Exception("密码必须包含至少一个字母")

    allowed_pattern = r'^[a-zA-Z0-9_*!]+$'
    if not re.match(allowed_pattern, user_password):
        raise Exception("密码只能包含字母、数字和'_'、'*'、'!'特殊字符")

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
        user_password = str(body.get('password'))

        with transaction.atomic():
            if user_accounts.objects.filter(user_email=user_email).exists():
                response['errorMessage'] = "邮箱已注册"
                return JsonResponse(response)

            # 验证邮箱，创建用户
            validate_email(user_email)
            user = user_accounts(
                user_email=user_email,
                user_name=user_name
            )
            # 验证密码复杂度
            validatePasswordComplexity(user_password)
            user.setPassword(user_password)
            user.save()

        response['status'] = 'SUCCESS'

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except EmailNotValidError as e:
        response['errorMessage'] = f"邮箱格式错误: {str(e)}"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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
        user_password = body.get('password')

        user = user_accounts.objects.get(user_email=user_email)
        if user.checkPassword(user_password):
            response['status'], response['user'] = 'SUCCESS', model_to_dict(user)
        else:
            response['errorMessage'] = "密码错误"
            return JsonResponse(response)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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
        user.user_balance = round(user.user_balance, 2)
        response['status'], response['user'] = 'SUCCESS', model_to_dict(user, exclude=['user_password'])
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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
        if new_balance <= 0:
            response['errorMessage'] = "无效余额"
            return JsonResponse(response)

        with transaction.atomic():
            user = user_accounts.objects.get(user_id=user_id)
            user.user_balance = new_balance
            user.save()
            response['status'], response['userID'] = 'SUCCESS', user_id

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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

        if user.checkPassword(old_password):
            with transaction.atomic():
                user = user_accounts.objects.get(user_id=user_id)
                validatePasswordComplexity(new_password)
                user.setPassword(new_password)
                user.save()

                response['status'] = 'SUCCESS'
                response['userID'] = user.user_id
        else:
            response['errorMessage'] = "旧密码错误"
            return JsonResponse(response)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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
        if not stock_ownerships.exists():
            response['status'] = "SUCCESS"
            return JsonResponse(response)

        stock_ownership_list = []
        for ownership in stock_ownerships:
            stock_ownership_map = model_to_dict(ownership, fields=['ownership_id', 'stock_code', 'stock_name', 'hold_number', 'purchase_per_price'])
            stock_ownership_map['purchase_per_price'] = round(stock_ownership_map['purchase_per_price'], 2)
            stock_ownership_list.append(stock_ownership_map)
        stock_ownership_list = sorted(stock_ownership_list, key=lambda x: x['hold_number'], reverse=True)

        response['status'], response['stockOwnershipList'] = "SUCCESS", stock_ownership_list

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

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
            stock_transaction_map['gains'], stock_transaction_map['transaction_date'] = round(stock_transaction_map['gains'], 5), user_transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S')
            stock_transaction_list.append(stock_transaction_map)
        response['status'], response['stockTransactionList'] = "SUCCESS", stock_transaction_list

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "用户不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def getFavoriteStocksInformation(request):
    ''' 获取用户自选股信息 '''

    response = {
       'status': 'ERROR',
       'errorMessage': None,
       'favoriteStocksList': None
    }
    try:
        user_id = request.GET.get('userID')
        favorite_stocks = user_favorite_stocks.objects.filter(user_id=user_id)

        if favorite_stocks.exists() == False:
            response['errorMessage'] = "用户没有添加自选股"
            return JsonResponse(response)

        favorite_stocks_list, query_stock_codes = [], ''
        for stock in favorite_stocks:
            stock_information = stock_basic.objects.get(stock_code=stock.stock_code)
            favorite_stocks_list.append(model_to_dict(stock_information, fields=['stock_code', 'stock_name', 'industry', 'area']))
            query_stock_codes += stock.stock_code + ','
        
        stocks_realtime_quote = ts.realtime_quote(ts_code=query_stock_codes[:-1])[['TS_CODE', 'PRE_CLOSE', 'PRICE', 'HIGH', 'LOW', 'VOLUME']]
        for i in range(len(favorite_stocks_list)):
            stock_map = stocks_realtime_quote.iloc[i].to_dict()
            if stock_map['TS_CODE'] == favorite_stocks_list[i]['stock_code']:
                favorite_stocks_list[i]['preClosePrice'], favorite_stocks_list[i]['currentPrice'] = stock_map['PRE_CLOSE'], stock_map['PRICE']
                favorite_stocks_list[i]['highPrice'], favorite_stocks_list[i]['lowPrice'] = stock_map['HIGH'], stock_map['LOW']
        
        response['status'], response['favoriteStocksList'] = "SUCCESS", favorite_stocks_list
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

'''
基础功能的页面展示效果较差，需要在用户的持有股查询和交易记录查询界面增加内容
持有股界面增加资产分布饼图和持仓时间散点图
交易记录界面增加交易收益折线图
'''

@csrf_exempt
@require_http_methods(['GET'])
def ownershipPageLoad(request):
    ''' 加载用户持有股页面的图表 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'assetDistributionMap': None,
        'holdTimeList': None
    }
    try:
        user_id = request.GET.get('userID')
        user_account = user_accounts.objects.get(user_id=user_id)
        user_ownerships = stock_ownership.objects.filter(user_id=user_id)
        assetDistributionMap, holdTimeList = {}, []

        assetDistributionMap['余额'] = round(user_account.user_balance, 2)
        for ownership in user_ownerships:
            assetDistributionMap[ownership.stock_name] = round(ownership.hold_number * ownership.purchase_per_price, 2)

            # 根据最早的交易记录来计算持仓时间
            first_buy_transaction = stock_transactions.objects.filter(
                user_id=user_account,
                stock_code=ownership.stock_code,
                transaction_type=0
            ).order_by('transaction_date').first()
            hold_hours = round((timezone.now() - first_buy_transaction.transaction_date).total_seconds() / 3600, 2)
            holdTimeList.append((ownership.purchase_per_price, hold_hours))

        # 将饼图中占比不在前十的，设置为其他
        sorted_assetDistributionMap = sorted(assetDistributionMap.items(), key=lambda item: item[1], reverse=True)
        if len(sorted_assetDistributionMap) > 10:
            top10 = dict(sorted_assetDistributionMap[:10])
            other_value = sum(value for _, value in sorted_assetDistributionMap[10:])
            assetDistributionMap = {**top10, '其他': round(other_value, 2)}
        else:
            assetDistributionMap = dict(sorted_assetDistributionMap)
        response['status'], response['assetDistributionMap'], response['holdTimeList'] = "SUCCESS", assetDistributionMap, holdTimeList
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def transactionPageLoad(request):
    ''' 加载用户交易记录界面的图表 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'transactionProfitList': None
    }
    try:
        user_id = request.GET.get('userID')
        user_transactions = stock_transactions.objects.filter(user_id=user_id)
        transactionProfitList = []

        for transaction in user_transactions:
            if transaction.gains != 0.0:
                formatted_date = transaction.transaction_date.strftime('%Y%m%d %H:%M')
                transactionProfitList.append((formatted_date, round(float(transaction.gains), 2)))

        response['status'], response['transactionProfitList'] = "SUCCESS", transactionProfitList
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['POST'])
def dialogueLocalModel(request):
    ''' 使用本地部署AI,进行决策问答(流式返回给前端) '''

    url = f"http://{os.getenv('BACKEND_IP')}:1500/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {"model": "deepseek-r1-distill-qwen-7b", "stream": True}
    try:
        body = json.loads(request.body.decode('utf-8'))
        content = body.get('content')
        data['messages'] = [{"role": "user", "content": content}]
        
        def stream_generator():
            with requests.post(url, headers=headers, json=data, stream=True) as response:
                response.encoding = 'utf-8'
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith('data: '):
                        continue
                    line = line[6:]
                    if line.strip() == '[DONE]':
                        break
                    try:
                        delta = json.loads(line)
                        if "choices" in delta and len(delta["choices"]) > 0:
                            content_piece = delta["choices"][0]["delta"].get("content", "")
                            yield f"data: {content_piece}\n\n"
                    except Exception as e:
                        yield f"data: [解析错误] {str(e)}\n\n"
        
        return StreamingHttpResponse(stream_generator(), content_type='text/event-stream; charset=utf-8')
    except Exception as e:
        return JsonResponse({'status': 'ERROR', 'errorMessage': str(e)})