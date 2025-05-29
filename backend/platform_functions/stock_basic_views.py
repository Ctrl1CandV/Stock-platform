from dotenv import load_dotenv
from datetime import time
import os, json
import warnings

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import user_accounts, stock_basic, stock_ownership, stock_transactions, stock_market, user_favorite_stocks
from utils.tools import tradable, get_previous_workday, ts, pro
from utils.response_view import api_view, APIException
from platform_functions import services

load_dotenv()
warnings.filterwarnings("ignore")

'''
证券查询页面主要包含，基于name或code的查询功能和股票的买入卖出功能
此外还需要进行股票列表的更新，设定为启动runserver时自动调用
'''
@ensure_csrf_cookie
def getCSRF(request):
    return JsonResponse({"detail": "CSRF cookie set"})

def updateStockBasic():
    ''' 更新股票列表 '''

    try:
        stock_basic.objects.first()
    except Exception as db_error:
        print(f"数据库未准备好，可能是数据迁移尚未完成: {str(db_error)}\n" + "请先完成数据迁移后再进行股票列表更新")
        return

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
    except Exception as e:
        print(f"股票列表更新失败: {str(e)}")

@api_view(methods=['GET'], require_token=False)
def isTrading(request, params):
    ''' 判断当前是否可以交易 '''
    if tradable():
        # 仅当可交易时，返回最新的每股价格
        stock_code = params.get('stockCode')
        quote = ts.realtime_quote(ts_code=stock_code)
        return { 'perPrice': round(quote['PRICE'][0], 2) }
    else:
        raise APIException("当前时间不允许交易")

# 模糊查询
@api_view(methods=['GET'], require_token=False)
def queryStockByName(request, params):
    ''' 根据股票名称查询 '''
    search_name = params.get('stockName')
    stock_basics = stock_basic.objects.filter(stock_name__contains=search_name)
    if not stock_basics.exists():
        raise APIException("查询结果为空")

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

    return { 'stockInformationList': stock_information_list }

# 精确搜索
@api_view(methods=['GET'], require_token=False)
def queryStockByCode(request, params):
    ''' 根据股票代码查询 '''
    search_code = params.get('stockCode')
    try:
        if search_code[-1].isalpha() and '.' in search_code:
            stock = stock_basic.objects.get(stock_code=search_code)
        else:
            stock = stock_basic.objects.get(stock_code__startswith=search_code)
    except ObjectDoesNotExist:
        raise APIException("该股票记录不存在")

    stock_information = {
        'stockCode': stock.stock_code,
        'stockName': stock.stock_name,
        'industry': stock.industry,
        'area': stock.area,
        'listDate': stock.list_date
    }
    return { 'stockInformation': stock_information} 

@api_view(methods=['POST'])
def buyStock(request, params):
    ''' 买入股票 '''
    user_id, stock_code, buy_number = params.get('userID'), params.get('stockCode'), params.get('buyNumber')
    # 购买数量区间判断
    if buy_number < 0 or buy_number > 10000:
        raise APIException("购买数量超出可交易区间")

    quote = ts.realtime_quote(ts_code=stock_code)
    if quote.empty or 'PRICE' not in quote:
        raise APIException("无法获取股票实时价格")

    # 余额判断
    per_price = round(quote['PRICE'][0], 2)
    total_amount = per_price * buy_number
    user = user_accounts.objects.get(user_id=user_id)
    if user.user_balance < total_amount:
        raise APIException("用户余额不足")

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

    return { 'userID': user.user_id, 'amountSpent': round(float(total_amount), 2) }

@api_view(methods=['POST'])
def sellStock(request, params):
    ''' 卖出持有股 '''
    ownership_id, sell_number = params.get('ownershipID'), params.get('sellNumber')
    user_ownership = stock_ownership.objects.get(ownership_id=ownership_id)
    if sell_number > user_ownership.hold_number:
        raise APIException("超出持有股的数量区间")

    with transaction.atomic():
        user = user_ownership.user_id
        quote = ts.realtime_quote(ts_code=user_ownership.stock_code)
        new_per_price = quote['PRICE'][0]

        gain = (new_per_price - user_ownership.purchase_per_price) * sell_number
        # 创建交易记录
        stock_transactions.objects.create(
            transaction_type=1,
            user_id=user,
            stock_code=user_ownership.stock_code,
            stock_name=user_ownership.stock_name,
            transaction_number=sell_number,
            per_price=new_per_price,
            gains=gain
        )

        # 更改持有股记录和用户余额
        user_ownership.hold_number -= sell_number
        user_ownership.save()
        if user_ownership.hold_number == 0:
            user_ownership.delete()
        user.user_balance += new_per_price * sell_number
        user.save()
    
    return { 'userID': user.user_id, 'gain': round(float(gain), 2) }

@api_view(methods=['POST'])
def addFavoriteStock(request, params):
    ''' 添加持有股 '''
    user_id, stock_code = params.get('userID'), params.get('stockCode')
    user_account = user_accounts.objects.get(user_id=user_id)

    # 进行数量和唯一性判断
    favorite_stocks = user_favorite_stocks.objects.filter(user_id=user_account)
    if favorite_stocks.exists():
        if favorite_stocks.count() > 50:
            raise APIException("自选股数量已达上限")
            
        if favorite_stocks.filter(stock_code=stock_code).exists():
            raise APIException("该股票已在自选股中")
        
    with transaction.atomic():
        user_favorite_stocks.objects.create(
            user_id=user_account,
            stock_code=stock_code
        )
    return {}

@api_view(methods=['POST'])
def removeFavoriteStock(request, params):
    ''' 删除持有股 '''
    user_id, stock_code = params.get('userID'), params.get('stockCode')
    user_account = user_accounts.objects.get(user_id=user_id)
        
    removeStock = user_favorite_stocks.objects.filter(
        user_id=user_account,
        stock_code=stock_code
    )
    if removeStock.exists():
        with transaction.atomic():
            removeStock.delete()
        return {}
    else:
        raise APIException("该股票不在自选股中")

@api_view(methods=['GET'], use_cache=True, cache_timeout=60 * 60, require_token=False)
def loadHomePageData(request, params, cache_manager):
    ''' 加载搜索主页的信息 '''
    Shanghai_top10, Shenzhen_top10 = {}, {}
    news_information, significant_index = {}, {}
    trade_date = get_previous_workday()

    # 上海十大成交股
    sh_top10_cache_key = f"sh_top10_{trade_date}"
    Shanghai_top10 = cache_manager.get_or_set(
        lambda: services._get_shanghai_top10(trade_date), 
        sh_top10_cache_key
    )

    # 深圳十大成交股
    sz_top10_cache_key = f"sz_top10_{trade_date}"
    Shenzhen_top10 = cache_manager.get_or_set(
        lambda: services._get_shenzhen_top10(trade_date), 
        sz_top10_cache_key
    )

    # 获取新闻信息
    news_cache_key = f"stock_news_{timezone.now().strftime('%Y-%m-%d %H')}"
    news_information = cache_manager.get_or_set(
        lambda: services._get_news_information(), 
        news_cache_key
    )

    # 获取重要指数信息
    index_cache_key = f"significant_index_{trade_date}"
    significant_index = cache_manager.get_or_set(
        lambda: services._get_significant_index(trade_date), 
        index_cache_key
    )

    return {
        'ShanghaiTop10': Shanghai_top10,
        'ShenzhenTop10': Shenzhen_top10,
        'newsInformation': news_information,
        'significantIndex': significant_index
    }