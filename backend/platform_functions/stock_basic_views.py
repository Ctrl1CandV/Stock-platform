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
from stock_analyse.functions import get_previous_workday
from user.validator import token_required
from .tushare_client import ts, pro

load_dotenv()
warnings.filterwarnings("ignore")

'''
证券查询页面主要包含，基于name或code的查询功能和股票的买入卖出功能
此外还需要进行股票列表的更新，设定为启动runserver时自动调用
'''
@ensure_csrf_cookie
def getCSRF(request):
    return JsonResponse({"detail": "CSRF cookie set"})

def tradable():
    # 测试模式不检查是否能够交易
    if os.getenv("RUN_MODE") == "TEST":
        return True

    now = timezone.now().time()
    is_trading_time = ((time(9, 30) <= now <= time(11, 30)) or
                       (time(13, 0) <= now <= time(15, 0)))
    
    if is_trading_time:
        today = timezone.now().strftime("%Y%m%d")
        trading = pro.trade_cal(exchange='', start_date=today, end_date=today)['is_open'][0]
        return bool(trading)
    else:
        return False

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

        print("股票列表更新成功")
    except Exception as e:
        print(f"股票列表更新失败: {str(e)}")

def cleanMarket():
    ''' 清理stock_market表  '''
    try:
        with transaction.atomic():
            stock_market.objects.all().delete()
        print("stock_market表已成功清除")
    except Exception as e:
        print(f"清除stock_market表错误: {str(e)}")

@require_http_methods(['GET'])
def isTrading(request):
    ''' 判断当前是否可以交易 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'perPrice': 0
    }
    try:
        if tradable():
            # 仅当可交易时，返回最新的每股价格
            stock_code = request.GET.get('stockCode')
            quote = ts.realtime_quote(ts_code=stock_code)
            response['status'], response['perPrice'] = 'SUCCESS', round(quote['PRICE'][0], 2)
        else:
            response['errorMessage'] = "当前时间不可交易"

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

# 模糊查询
@require_http_methods(['GET'])
def queryStockByName(request):
    ''' 根据股票名称查询 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'stockInformationList': None
    }
    try:
        search_name = request.GET.get('stockName')
        stock_basics = stock_basic.objects.filter(stock_name__contains=search_name)
        if not stock_basics.exists():
            response['errorMessage'] = "查询结果为空"
            return JsonResponse(response)

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
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

# 精确搜索
@require_http_methods(['GET'])
def queryStockByCode(request):
    ''' 根据股票代码查询 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'stockInformation': None
    }
    try:
        search_code = request.GET.get('stockCode')
        if search_code[-1].isalpha() and '.' in search_code:
            stock = stock_basic.objects.get(stock_code=search_code)
        else:
            stock = stock_basic.objects.get(stock_code__startswith=search_code)

        stock_information = {
                'stockCode': stock.stock_code,
                'stockName': stock.stock_name,
                'industry': stock.industry,
                'area': stock.area,
                'listDate': stock.list_date
            }
        response['status'], response['stockInformation'] = 'SUCCESS', [stock_information]

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "该股票代码不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@require_http_methods(['POST'])
@token_required
def buyStock(request):
    ''' 买入股票 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None,
        'amountSpent': None
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        stock_code = body.get('stockCode')
        buy_number = body.get('buyNumber')

        # 交易时间判断
        if not tradable():
            response['errorMessage'] = "当前时间不允许交易"
            return JsonResponse(response)

        # 购买数量区间判断
        if buy_number < 0 or buy_number > 10000:
            response['errorMessage'] = "购买数量超出可交易区间"
            return JsonResponse(response)

        # 余额判断
        quote = ts.realtime_quote(ts_code=stock_code)
        if quote.empty or 'PRICE' not in quote:
            response['errorMessage'] = "无法获取股票实时价格"
            return JsonResponse(response)

        per_price = round(quote['PRICE'][0], 2)
        total_amount = per_price * buy_number
        user = user_accounts.objects.get(user_id=user_id)
        if user.user_balance < total_amount:
            response['errorMessage'] = "用户余额不足"
            return JsonResponse(response)

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

            response['status'], response['userID'], response['amountSpent'] = "SUCCESS", user.user_id, round(float(total_amount), 2)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "该股票记录不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@require_http_methods(['POST'])
@token_required
def sellStock(request):
    ''' 卖出持有股 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'userID': None,
        'gain': 0
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        ownership_id = body.get('ownershipID')
        sell_number = body.get('sellNumber')
        user_ownership = stock_ownership.objects.get(ownership_id=ownership_id)

        # 交易时间判断
        if not tradable():
            response['errorMessage'] = "当前时间不允许交易"
            return JsonResponse(response)

        if sell_number > user_ownership.hold_number:
            response['errorMessage'] = "超出持有股的数量区间"
            return JsonResponse(response)

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
            response['status'], response['userID'], response['gain'] = "SUCCESS", user.user_id, round(float(gain), 2)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except ObjectDoesNotExist:
        response['errorMessage'] = "该持有股记录不存在"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@require_http_methods(['POST'])
@token_required
def addFavoriteStock(request):
    ''' 添加持有股 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        stock_code = body.get('stockCode')
        user_account = user_accounts.objects.get(user_id=user_id)

        # 进行数量和唯一性判断
        favorite_stocks = user_favorite_stocks.objects.filter(user_id=user_account)
        if favorite_stocks.exists():
            if favorite_stocks.count() > 50:
                response['errorMessage'] = "自选股数量已达上限"
                return JsonResponse(response)
            
            if favorite_stocks.filter(stock_code=stock_code).exists():
                response['errorMessage'] = "该股票已在自选股中"
                return JsonResponse(response)
        
        with transaction.atomic():
            user_favorite_stocks.objects.create(
                user_id=user_account,
                stock_code=stock_code
            )

        response['status'] = 'SUCCESS'
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@require_http_methods(['POST'])
@token_required
def removeFavoriteStock(request):
    ''' 删除持有股 '''

    response = {
       'status': 'ERROR',
       'errorMessage': None,
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_id = body.get('userID')
        stock_code = body.get('stockCode')
        user_account = user_accounts.objects.get(user_id=user_id)
        
        removeStock = user_favorite_stocks.objects.filter(
            user_id=user_account,
            stock_code=stock_code
        )
        if removeStock.exists():
            with transaction.atomic():
                removeStock.delete()
            response['status'] = 'SUCCESS'
        else:
            response['errorMessage'] = "该股票不在自选股中"

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@require_http_methods(['GET'])
def loadHomePageData(request):
    ''' 加载搜索主页的信息 '''

    response = {
       'status': 'ERROR',
       'errorMessage': None,
       'ShanghaiTop10': None,
       'ShenzhenTop10': None,
       'newsInformation': None,
       'significantIndex': None
    }
    try:
        Shanghai_top10, Shenzhen_top10 = {}, {}
        news_information, significant_index = {}, {}
        trade_date = get_previous_workday()

        # 新增缓存key
        sh_top10_cache_key = f"sh_top10_{trade_date}"
        sz_top10_cache_key = f"sz_top10_{trade_date}"
        index_cache_key = f"significant_index_{trade_date}"
        news_cache_key = f"stock_news_{timezone.now().strftime('%Y-%m-%d %H')}"

        # 上海十大成交股缓存
        Shanghai_top10 = cache.get(sh_top10_cache_key)
        if Shanghai_top10 is None:
            Shanghai_data = pro.hsgt_top10(trade_date=trade_date, market_type='1')[['name', 'amount']].sort_values('amount', ascending=False)
            Shanghai_data['amount'] = Shanghai_data['amount'].apply(lambda x: f'{x / 100000000:.2f}亿')
            Shanghai_top10 = Shanghai_data.set_index('name')['amount'].to_dict()
            cache.set(sh_top10_cache_key, Shanghai_top10, timeout=24 * 3600)

        # 深圳十大成交股缓存
        Shenzhen_top10 = cache.get(sz_top10_cache_key)
        if Shenzhen_top10 is None:
            Shenzhen_data = pro.hsgt_top10(trade_date=trade_date, market_type='3')[['name', 'amount']].sort_values('amount', ascending=False)
            Shenzhen_data['amount'] = Shenzhen_data['amount'].apply(lambda x: f'{x / 100000000:.2f}亿')
            Shenzhen_top10 = Shenzhen_data.set_index('name')['amount'].to_dict()
            cache.set(sz_top10_cache_key, Shenzhen_top10, timeout=24 * 3600)

        # 获取新闻信息
        news_information = cache.get(news_cache_key)
        if news_information is None:
            news_data = pro.news(src='eastmoney', start_date=timezone.now().strftime('%Y-%m-%d') + ' 00:00:00', fields='datetime,content').head(10)
            news_information = news_data.set_index('datetime')['content'].to_dict()
            cache.set(news_cache_key, news_information, timeout=24 * 3600)

        # 获取上证指数、深证成指、创业板指的最新行情
        significant_index = cache.get(index_cache_key)
        if significant_index is None:
            shanghai = pro.index_daily(ts_code='000001.SH', trade_date=trade_date)
            SZSE = pro.index_daily(ts_code='399001.SZ', trade_date=trade_date)
            GEM = pro.index_daily(ts_code='399006.SZ', trade_date=trade_date)

            if not shanghai.empty:
                shanghai = shanghai.iloc[0]
                sh_val = round((shanghai['close'] - shanghai['pre_close']) / shanghai['pre_close'] * 100, 4)
            else:
                sh_val = 0

            if not SZSE.empty:
                SZSE = SZSE.iloc[0]
                sz_val = round((SZSE['close'] - SZSE['pre_close']) / SZSE['pre_close'] * 100, 4)
            else:
                sz_val = 0

            if not GEM.empty:
                GEM = GEM.iloc[0]
                gem_val = round((GEM['close'] - GEM['pre_close']) / GEM['pre_close'] * 100, 4)
            else:
                gem_val = 0

            significant_index = {
                '上证指数': sh_val,
                '深证成指': sz_val,
                '创业板指': gem_val
            }
            cache.set(index_cache_key, significant_index, timeout=24 * 3600)

        response['status'], response['ShanghaiTop10'], response['ShenzhenTop10'], response['newsInformation'], response['significantIndex'] = 'SUCCESS', Shanghai_top10, Shenzhen_top10, news_information, significant_index
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)