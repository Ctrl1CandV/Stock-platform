from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from platform_functions.models import stock_market
from django.http import JsonResponse
from django.core.cache import cache
from . import functions
import pandas as pd
import datetime
import json

@csrf_exempt
@require_http_methods(['GET'])
def forecastStock(request):
    ''' 使用Transformer进行股票收盘价的预测 '''

    response = {
        'status': 'ERROR',
        'result': None,
        'gainRate': None,
        'errorMessage': None
    }
    try:
        stock_code = request.GET.get('stockCode')

        # 数据缓存判断
        cache_key = f'forecastStock_{stock_code}'
        cache_result = cache.get(cache_key)
        if cache_result:
            return JsonResponse(cache_result)

        stock_markets = stock_market.objects.filter(stock_code=stock_code).order_by('trade_date')
        if stock_markets.exists():
            data = pd.DataFrame(list(stock_markets.values()))
            gain_rate, result = functions.forecast_result(stock_code, data)
        else:
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=500)
            start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
            data = functions.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            gain_rate, result = functions.forecast_result(stock_code, data)

        response['status'], response['result'], response['gainRate'] = 'SUCCESS', float(result), float(gain_rate)
        cache.set(cache_key, response, timeout=60 * 60)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def showZScore(request):
    ''' 展示股票的Z分模型得分 '''

    response = {
        'status': 'ERROR',
        'zScore': None,
        'X': None,
        'errorMessage': None
    }
    try:
        stock_code = request.GET.get('stockCode')

        # 数据缓存判断
        cache_key = f'showZScore_{stock_code}'
        cache_result = cache.get(cache_key)
        if cache_result:
            return JsonResponse(cache_result)

        z_score, X = functions.calculate_Zscore(stock_code)
        response['status'], response['zScore'], response['X'] = 'SUCCESS', z_score, X
        cache.set(cache_key, response, timeout=60 * 60)
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def showSharpeRatio(request):
    ''' 展示夏普比率和当前的国债利率 '''

    response = {
        'status': 'ERROR',
        'sharpeRatio': None,
        'rateMap': None,
        'errorMessage': None
    }
    try:
        stock_code = request.GET.get('stockCode')

        # 数据缓存判断
        cache_key = f'showSharpeRatio_{stock_code}'
        cache_result = cache.get(cache_key)
        if cache_result:
            return JsonResponse(cache_result)

        stock_markets = stock_market.objects.filter(stock_code=stock_code).order_by('trade_date')
        # 数据库中没有数据则通过Tushare获取
        if stock_markets.exists():
            data = pd.DataFrame(list(stock_markets.values()))
        else:
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=500)
            start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
            data = functions.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)

        rate_map = functions.crawling_riskfree_rate()
        rate, sharpe_ratio = functions.calculate_sharpe_ratio(float(rate_map['10年']), data['pct_chg'])
        rate_map[f'{stock_code}'] = rate
        response['status'], response['sharpeRatio'], response['rateMap'] = 'SUCCESS', sharpe_ratio ,rate_map
        cache.set(cache_key, response, timeout=60 * 60)

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response, status=400)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response, status=500)

    return JsonResponse(response)