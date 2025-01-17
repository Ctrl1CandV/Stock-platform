from .models import user_accounts, stock_basic, stock_ownership, stock_transactions
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db import transaction
from datetime import time
import tushare as ts
import datetime
import json

import warnings
warnings.filterwarnings("ignore")

token = '66e72ae286def4e5826d1edc84f45cdad596c34137a91396b335cefd'
pro = ts.pro_api(token)

'''
证券查询页面主要包含，基于name或code的查询功能和股票的买入卖出功能
此外还需要进行股票列表的更新，设定为启动runserver时自动调用
'''
def tradable():
    now = datetime.datetime.now().time()
    is_trading_time = ((time(9, 30) <= now <= time(11, 30)) or
                       (time(13, 0) <= now <= time(15, 0)))

    if is_trading_time:
        today = datetime.datetime.today().strftime("%Y%m%d")
        trading = pro.trade_cal(exchange='', start_date=today, end_date=today)['is_open'][0]
        return bool(trading)
    else:
        return False

def updateStockBasic():
    ''' 更新股票列表 '''

    try:
        new_stock_basic = pro.stock_basic(
            exchange='', list_status='L',
            fields='ts_code, name, area, industry, list_date'
        )
        if new_stock_basic.empty:
            print("未获取到新的股票列表数据")
            return

        with transaction.atomic():
            # 清除旧数据
            stock_basic.objects.all().delete()

            new_records = [
                stock_basic(
                    stock_code=row['ts_code'],
                    stock_name=row['name'],
                    industry=row['industry'],
                    area=row['area'],
                    list_date=row['list_date']
                )
                for index, row in new_stock_basic.iterrows()
            ]

            # 使用批处理进行数据插入
            stock_basic.objects.bulk_create(new_records)

        print("股票列表更新成功")
    except Exception as e:
        print(f"股票列表更新失败: {str(e)}")

@csrf_exempt
@require_http_methods(['GET'])
def isTrading(request):
    ''' 判断当前是否可以交易 '''

    response = {
        'status': False,
        'errorMessage': None,
        'perPrice': 0
    }
    try:
        if tradable():
            # 仅当可交易时，返回最新的每股价格
            body = json.loads(request.body.decode('utf-8'))
            stock_code = body.get('stockCode')
            quote = ts.realtime_quote(ts_code=stock_code)
            response['status'], response['perPrice'] = True, quote['PRICE'][0]

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

# 模糊查询
@csrf_exempt
@require_http_methods(['GET'])
def queryStockByName(request):
    ''' 根据股票名称查询 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'stockInformationList': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        search_name = body.get('stockName')
        stock_basics = stock_basic.objects.filter(stock_name__contains=search_name)

        stock_information_list = []
        for stock in stock_basics:
            stock_information_map = {
            'stockCode': stock.stock_code,
            'stockName': stock.stock_name,
            'industry': stock.industry,
            'area': stock.area,
            'listDate': stock.list_date
            }
            stock_information_list.append(stock_information_map)

        response['status'], response['stockInformationList'] = 'SUCCESS', stock_information_list

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

# 精确搜索
@csrf_exempt
@require_http_methods(['GET'])
def queryStockByCode(request):
    ''' 根据股票代码查询 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'stockInformation': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        search_code = body.get('stockCode')
        stock = stock_basic.objects.get(stock_code=search_code)
        stock_information = {
            'stockCode': stock.stock_code,
            'stockName': stock.stock_name,
            'industry': stock.industry,
            'area': stock.area,
            'listDate': stock.list_date
        }
        response['status'], response['stockInformation'] = 'SUCCESS', stock_information

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except ObjectDoesNotExist:
        response['errorMessage'] = "该股票代码不存在"
        return JsonResponse(response, status=404)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['POST'])
def buyStock(request):
    ''' 买入股票 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        stock_code = body.get('stockCode')
        buy_number = body.get('buyNumber')

        # 交易时间判断
        if not tradable():
            response['errorMessage'] = "当前时间不允许交易"
            return JsonResponse(response, status=400)

        # 购买数量区间判断
        if buy_number < 0 or buy_number > 10000:
            response['errorMessage'] = "购买数量超出可交易区间"
            return JsonResponse(response, status=400)

        # 余额判断
        quote = ts.realtime_quote(ts_code=stock_code)
        if quote.empty or 'PRICE' not in quote:
            response['errorMessage'] = "无法获取股票实时价格"
            return JsonResponse(response, status=400)

        per_price = quote['PRICE'][0]
        total_amount = per_price * buy_number
        user = user_accounts.objects.get(user_id=user_id)
        if user.user_balance < total_amount:
            response['errorMessage'] = "用户余额不足"
            return JsonResponse(response, status=400)

        with (transaction.atomic()):
            stock_information = stock_basic.objects.get(stock_code=stock_code)

            # 创造交易记录
            stock_transactions.objects.create(
                transaction_type=0,
                user_id=user,
                stock_code=stock_code,
                stock_name=stock_information.stock_name,
                transaction_number=buy_number,
                per_price=per_price,
                gains=0
            )

            '''
            对已经持有的股票，在持有基础上进行叠加，单价采用加权和形式
            对未持有的股票，直接创建一个持有股记录即可
            '''
            user_ownership, created = stock_ownership.objects.get_or_create(
                user_id=user,
                stock_code=stock_code,
                defaults={
                    'stock_name': stock_information.stock_name,
                    'hold_number': buy_number,
                    'purchase_per_price': per_price
                }
            )
            if not created:
                user_ownership.purchase_per_price = (user_ownership.purchase_per_price * user_ownership.hold_number + total_amount) / (user_ownership.hold_number + buy_number)
                user_ownership.hold_number += buy_number
                user_ownership.save()

            # 余额扣除
            user.user_balance -= total_amount
            user.save()

            response['status'], response['userID'] = "SUCCESS", user.user_id

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except ObjectDoesNotExist:
        response['errorMessage'] = "该股票记录不存在"
        return JsonResponse(response, status=404)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['POST'])
def sellStock(request):
    ''' 卖出持有股 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        ownership_id = body.get('ownershipID')
        sell_number = body.get('sellNumber')
        user_ownership = stock_ownership.objects.get(ownership_id=ownership_id)

        # 交易时间判断
        if not tradable():
            response['errorMessage'] = "当前时间不允许交易"
            return JsonResponse(response, status=400)

        if sell_number > user_ownership.hold_number:
            response['errorMessage'] = "超出持有股的数量区间"
            return JsonResponse(response, status=400)

        with transaction.atomic():
            user = user_accounts.objects.get(user_id=user_ownership.user_id)
            quote = ts.realtime_quote(ts_code=user_ownership.stock_code)
            new_per_price = quote['PRICE'][0]

            # 创建交易记录
            stock_transactions.objects.create(
                transaction_type=1,
                user_id=user,
                stock_code=user_ownership.stock_code,
                stock_name=user_ownership.stock_name,
                transaction_number=sell_number,
                per_price=new_per_price,
                gains=(new_per_price - user_ownership.purchase_per_price) * sell_number
            )

            # 更改持有股记录和用户余额
            user_ownership.hold_number -= sell_number
            user_ownership.save()
            if user_ownership.hold_number == 0:
                user_ownership.delete()
            user.user_balance += new_per_price * sell_number
            user.save()
            response['status'], response['userID'] = "SUCCESS", user.user_id

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except ObjectDoesNotExist:
        response['errorMessage'] = "该持有股记录不存在"
        return JsonResponse(response, status=404)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)