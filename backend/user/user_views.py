from email_validator import validate_email, EmailNotValidError
import os, json, requests
import jwt, time

from .models import user_accounts, stock_ownership, stock_transactions, user_favorite_stocks, stock_basic
from utils.tools import validatePasswordComplexity, send_verification_code_code, ts, pro
from utils.response_view import api_view, APIException

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, StreamingHttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.conf import settings

'''
用户模块功能：
1. 注册、登录和个人信息补充
2. 账号名、密码和余额更改
3. 股票持仓查询
4. 证券交易记录查询
'''
@api_view(methods=['GET'], require_token=False)
def sendVerificationCode(request, params):
    ''' 发送邮箱验证码 '''
    user_email = params.get('userEmail')
    try:
        validate_email(user_email)
    except EmailNotValidError:
        raise APIException("邮箱格式错误")

    status, verification_code = send_verification_code_code(user_email)
    if status:
        cache.set(f"{user_email}_code", verification_code, timeout=60 * 2)
        return { 'verificationCode': verification_code }
    else:
        raise APIException("验证码发送失败")

@api_view(methods=['POST'], require_token=False)
def register(request, params):
    ''' 用户注册 '''
    user_email, user_name, user_password = params.get('userEmail'), params.get('userName'), str(params.get('password'))
    verification_code = str(body.get('verificationCode'))

    try:
        validate_email(user_email)
    except EmailNotValidError:
        raise APIException("邮箱格式错误")

    email_code = cache.get(f"{user_email}_code")
    if email_code is None or email_code != verification_code:
        raise APIException("验证码错误")

    if user_accounts.objects.filter(user_email=user_email).exists():
        raise APIException("邮箱已注册")

    with transaction.atomic():

        # 验证邮箱，创建用户
        user = user_accounts(
            user_email=user_email,
            user_name=user_name
        )
        # 验证密码复杂度
        validatePasswordComplexity(user_password)
        user.setPassword(user_password)
        user.save()

    return {}

@api_view(methods=['POST'], use_cache=True, cache_timeout=7 * 24 * 60 * 60, require_token=False)
def login(request, params, cache_manager):
    ''' 用户登录 '''
    user_email, user_password = params.get('userAccount'), params.get('password')
    try:
        user = user_accounts.objects.get(user_email=user_email)
    except ObjectDoesNotExist:
        raise APIException("用户不存在")
    if user.checkPassword(user_password):
        def get_login_data():
            # 使用JWT生成Token，过期时间为七天
            current_time = int(time.time())
            expire_time = current_time + 7 * 24 * 60 * 60

            payload = {
                'user_id': user.user_id,
                'email': user.user_email,
                'exp': expire_time,
                'iat': current_time
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return token

        token = cache_manager.get_or_set(get_login_data, f'user_{user.user_id}_token')
        return { 'Token': token, 'user': model_to_dict(user) }
    else:
        raise APIException("密码错误")

@api_view(methods=['GET'])
def gainUserInformation(request, params):
    ''' 获取用户个人信息 '''
    user_id = params.get('userID')
    user = user_accounts.objects.get(user_id=user_id)
    user.user_balance = round(user.user_balance, 2)
    return { 'user': model_to_dict(user, exclude=['user_password']) }

@api_view(methods=['POST'])
def updateProfile(request, params):
    ''' 补充用户个人信息 '''
    user_data, user_id = params.get('userData'), params.get('userID')
    user = user_accounts.objects.get(user_id=user_id)

    with transaction.atomic():
        # 当键名等于属性名时，将键对应值赋予属性
        for field, value in user_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()
    return { 'userID': user_id }

@api_view(methods=['POST'])
def updateBalance(request, params):
    ''' 更新用户余额 '''
    user_id, new_balance = params.get('userID'), float(params.get('newBalance'))
    user = user_accounts.objects.get(user_id=user_id)
    if new_balance <= 0:
        raise APIException("无效余额")

    with transaction.atomic():
        user.user_balance = new_balance
        user.save()
    return { 'userID': user_id }

@api_view(methods=['POST'])
def changePassword(request, params):
    ''' 修改用户密码 '''
    user_id = params.get('userID')
    user = user_accounts.objects.get(user_id=user_id)
    old_password, new_password = params.get('oldPassword'), params.get('newPassword')
    if user.checkPassword(old_password):
        with transaction.atomic():
            validatePasswordComplexity(new_password)
            user.setPassword(new_password)
            user.save()
    else:
        raise APIException("旧密码错误")

    return { 'userID': user_id }

# 用户股票模块的功能
@api_view(methods=['GET'])
def getStockOwnership(request, params):
    ''' 查询用户股票持仓 '''
    user_id = params.get('userID')
    stock_ownerships = stock_ownership.objects.filter(user_id=user_id)
    if not stock_ownerships.exists():
        return { 'stockOwnershipList': [] }

    stock_ownership_list = []
    for ownership in stock_ownerships:
        stock_ownership_map = model_to_dict(ownership, fields=['ownership_id', 'stock_code', 'stock_name', 'hold_number', 'purchase_per_price'])
        stock_ownership_map['purchase_per_price'] = round(stock_ownership_map['purchase_per_price'], 2)
        stock_ownership_list.append(stock_ownership_map)
    stock_ownership_list = sorted(stock_ownership_list, key=lambda x: x['hold_number'], reverse=True)
    return { 'stockOwnershipList': stock_ownership_list }

@api_view(methods=['GET'])
def getTransactionRecords(request, params):
    ''' 查询用户交易记录 '''
    user_id = params.get('userID')
    user_transactions = stock_transactions.objects.filter(user_id=user_id)

    stock_transaction_list = []
    for user_transaction in user_transactions:
        stock_transaction_map = model_to_dict(
            user_transaction,
            fields=['transaction_type', 'stock_code', 'stock_name', 'transaction_number', 'per_price', 'gains']
        )
        stock_transaction_map['gains'], stock_transaction_map['transaction_date'] = round(stock_transaction_map['gains'], 5), user_transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S')
        stock_transaction_list.append(stock_transaction_map)
    return { 'stockTransactionList': stock_transaction_list }

@api_view(methods=['GET'])
def getFavoriteStocksInformation(request, params):
    ''' 获取用户自选股信息 '''
    user_id = params.get('userID')
    favorite_stocks = user_favorite_stocks.objects.filter(user_id=user_id)
    if favorite_stocks.exists() == False:
        return { 'favoriteStocksList': [] }

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
        
    return { 'favoriteStocksList': favorite_stocks_list }

'''
基础功能的页面展示效果较差，需要在用户的持有股查询和交易记录查询界面增加内容
持有股界面增加资产分布饼图和持仓时间散点图
交易记录界面增加交易收益折线图
'''
@api_view(methods=['GET'])
def ownershipPageLoad(request, params):
    ''' 加载用户持有股页面的图表 '''
    user_id = params.get('userID')
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
    return { 'assetDistributionMap': assetDistributionMap, 'holdTimeList': holdTimeList }

@api_view(methods=['GET'])
def transactionPageLoad(request, params):
    ''' 加载用户交易记录界面的图表 '''
    user_id = params.get('userID')
    user_transactions = stock_transactions.objects.filter(user_id=user_id)
    transactionProfitList = []

    for transaction in user_transactions:
        if transaction.gains != 0.0:
            formatted_date = transaction.transaction_date.strftime('%Y%m%d %H:%M')
            transactionProfitList.append((formatted_date, round(float(transaction.gains), 2)))

    return { 'transactionProfitList': transactionProfitList }

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