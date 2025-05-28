from decimal import Decimal, getcontext
import pandas as pd
import numpy as np
import datetime
import json

from platform_functions.models import stock_market
from utils.response_view import api_view
from django.utils import timezone
from . import functions

@api_view(methods=['GET'], use_cache=True, cache_timeout=60 * 60, require_token=False)
def forecastStock(request, params, cache_manager):
    ''' 使用Transformer进行股票收盘价的预测 '''
    stock_code = params.get('stockCode')
    
    def get_forecast_stock():
        stock_markets = stock_market.objects.filter(stock_code=stock_code).order_by('trade_date')
        if stock_markets.exists():
            data = pd.DataFrame(list(stock_markets.values()))
            gain_rate, result = functions.forecast_result(stock_code, data)
        else:
            end_date = timezone.now().date()
            start_date = end_date - datetime.timedelta(days=500)
            start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
            data = functions.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            gain_rate, result = functions.forecast_result(stock_code, data)

        return round(float(result), 4), round(float(gain_rate), 5)
    
    result, gain_rate = cache_manager.get_or_set(get_forecast_stock)
    return { 'result': result, 'gainRate': gain_rate }

@api_view(methods=['GET'], use_cache=True, cache_timeout=60 * 60, require_token=False)
def showZScore(request, params, cache_manager):
    ''' 展示股票的Z分模型得分 '''
    stock_code = params.get('stockCode')

    def get_zscore():
        z_score, X = functions.calculate_Zscore(stock_code)
        # 缺值判断和处理
        z_score = "数据缺失" if np.isnan(z_score) else round(float(z_score), 4)
        for i in range(len(X)):
            X[i] = np.float64(0) if np.isnan(X[i]) else round(float(X[i]), 4)
        return z_score, X
            
    z_score, X = cache_manager.get_or_set(get_zscore)
    return {'zScore': z_score, 'X': X }

@api_view(methods=['GET'], use_cache=True, cache_timeout=60 * 60, require_token=False)
def showSharpeRatio(request, params, cache_manager):
    ''' 展示夏普比率和当前的国债利率 '''
    stock_code = params.get('stockCode')

    def get_sharpe_ratio():
        stock_markets = stock_market.objects.filter(stock_code=stock_code).order_by('trade_date')
        # 数据库中没有数据则通过Tushare获取
        if stock_markets.exists():
            data = pd.DataFrame(list(stock_markets.values()))
        else:
            end_date = timezone.now().date()
            start_date = end_date - datetime.timedelta(days=500)
            start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
            data = functions.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)

        rate_map = functions.crawling_riskfree_rate()
        rate, sharpe_ratio = functions.calculate_sharpe_ratio(float(rate_map['10年']), data['pct_chg'])
        rate_map[f'{stock_code}'] = rate
        return sharpe_ratio, rate_map

    sharpe_ratio, rate_map = cache_manager.get_or_set(get_sharpe_ratio)
    return {'sharpeRatio': sharpe_ratio, 'rateMap': rate_map }