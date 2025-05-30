import pandas as pd
import datetime
import json

from utils.response_view import api_view, APIResponse, APIException
from platform_functions import services
from django.db import transaction
from django.utils import timezone
from .models import stock_market
from utils.tools import ts, pro
from utils.logger import logger

'''
股票详细页面的显示内容包含
股票行情图、技术指标图、市盈率市净率变化图和公司财务数据
'''
@api_view(methods=['POST'], require_token=False)
def updateAnnualDailyQuotes(request, params):
    ''' 获取年度日线行情并保存本地，用于模型训练和夏普比例的计算 '''
    stock_code = params.get('stockCode')
    try:
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=500)
        start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
        stock_daily = services.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        stock_daily = stock_daily[['trade_date', 'open', 'high', 'low', 'close', 'pct_chg', 'vol', 'amount']]
        with transaction.atomic():
            # 删去冗余数据
            stock_market.objects.filter(stock_code=stock_code).delete()

            new_market_records = [
                stock_market(
                    stock_code=stock_code,
                    trade_date=row['trade_date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    pct_chg=row['pct_chg'],
                    vol=row['vol'],
                    amount=row['amount']
                )
                for index, row in stock_daily.iterrows()
            ]

            stock_market.objects.bulk_create(new_market_records)
        logger.info(f"{stock_code}的年度日线行情已保存本地")
        return APIResponse(status="SUCCESS").to_json()
    except Exception as e:
        logger.error(f"股票年度日线行情更新失败: {str(e)}")
        raise APIException(message="股票日线行情更新失败")

@api_view(methods=['GET'], use_cache=True, require_token=False)
def showStockQurve(request, params, cache_manager):
    ''' 显示日、周和月的行情数据 '''
    stock_code = params.get('stockCode')
    time_span, time_type = int(params.get('timeSpan')), int(params.get('type'))
    if time_span <= 0 or time_span >= 3000:
        raise APIException(message="无效的时间跨度")
    
    data, title = cache_manager.get_or_set(lambda: services.get_stock_data(stock_code, time_span, time_type))
    return { 'data': data, 'title': title }

@api_view(methods=['GET'], use_cache=True, require_token=False)
def showTechnicalIndicator(request, params, cache_manager):
    ''' 展示技术指标的变化图 '''
    stock_code = params.get('stockCode')

    def get_indicator_data():
        stock_markets = stock_market.objects.filter(stock_code=stock_code).order_by('trade_date')
        if stock_markets.exists():
            data = pd.DataFrame(list(stock_markets.values('trade_date', 'high', 'low', 'close')))
            data.rename(columns={
                'trade_date': 'trade_date',
                'high': 'high',
                'low': 'low',
                'close': 'close'
            }, inplace=True)
            indicator_data = services.technical_indicator_data(stock_code, data)
        else:
            indicator_data = services.technical_indicator_data(stock_code)
        return indicator_data

    indicator_data = cache_manager.get_or_set(get_indicator_data)
    return { 'indicatorData': indicator_data }

@api_view(methods=['GET'], use_cache=True, require_token=False)
def getFinancialMetric(request, params, cache_manager):
    ''' 获取公司财务指标数据 '''
    stock_code = params.get('stockCode')
    financial_metric_map = cache_manager.get_or_set(lambda: services.financial_metric_form(stock_code))
    return { 'financialMetricMap': financial_metric_map }

@api_view(methods=['GET'], use_cache=True, require_token=False)
def showValuationRatio(request, params, cache_manager):
    ''' 展示股票估值比率的变化图 '''
    stock_code = params.get('stockCode')
    valuation_data = cache_manager.get_or_set(lambda: services.valuation_ratio_data(stock_code))
    return { 'valuationData': valuation_data }

@api_view(methods=['GET'], use_cache=True, require_token=False)
def gainIntroduction(request, params, cache_manager):
    ''' 获取公司简介信息 '''
    stock_code = params.get('stockCode')
    introduction = cache_manager.get_or_set(lambda: pro.stock_company(ts_code=stock_code, fields='ts_code,introduction'))["introduction"][0]
    return { 'introduction': introduction }

@api_view(methods=['GET'], use_cache=True, require_token=False)
def getBasicMetrics(request, params, cache_manager):
    ''' 获取股票的基本指标信息 '''
    stock_code = params.get('stockCode')
    basic_metrics = cache_manager.get_or_set(lambda: services._get_basic_metrics(stock_code))
    return basic_metrics