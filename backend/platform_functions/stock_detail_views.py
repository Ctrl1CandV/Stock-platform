from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import stock_detail_functions
from .tushare_client import ts, pro
from django.db import transaction
from django.utils import timezone
from .models import stock_market
import datetime
import json

'''
股票详细页面的显示内容包含
股票行情图、技术指标图、市盈率市净率变化图和公司财务数据
'''

@csrf_exempt
@require_http_methods(['POST'])
def updateAnnualDailyQuotes(request):
    ''' 获取年度日线行情并保存本地，用于模型训练和夏普比例的计算 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
    }
    try:
        body = json.loads(request.body.decode('utf-8'))
        stock_code = body.get('stockCode')

        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=500)
        start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
        stock_daily = stock_detail_functions.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
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

        response['status'] = "SUCCESS"
        print(f"{stock_code}的年度日线行情已保存本地")
    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        print(f"股票年度日线行情更新失败: {str(e)}")

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def showStockQurve(request):
    ''' 显示日、周和月的行情数据 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'image': None,
    }
    try:
        stock_code = request.GET.get('stockCode')
        time_span = int(request.GET.get('timeSpan'))
        type = int(request.GET.get('type'))

        # type用int表示，1对应日线，2对应周线，3对应月线
        image = stock_detail_functions.get_stock_chart(stock_code, time_span, type)
        response['status'], response['image'] = 'SUCCESS', image

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def showTechnicalIndicator(request):
    ''' 展示技术指标的变化图 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'indicatorCharts': None,
    }
    try:
        stock_code = request.GET.get('stockCode')
        charts = stock_detail_functions.technical_indicator_charts(stock_code)
        response['status'], response['indicatorCharts'] = 'SUCCESS', charts

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def getFinancialMetric(request):
    ''' 获取公司财务指标数据 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'financialMetricMap': None,
    }
    try:
        stock_code = request.GET.get('stockCode')
        financial_metric_map = stock_detail_functions.financial_metric_form(stock_code)
        response['status'], response['financialMetricMap'] = 'SUCCESS', financial_metric_map

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def showValuationRatio(request):
    ''' 展示股票估值比率的变化图 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'valuationRatioImage': None,
    }
    try:
        stock_code = request.GET.get('stockCode')
        image = stock_detail_functions.valuation_ratio_charts(stock_code)
        response['status'], response['valuationRatioImage'] = 'SUCCESS', image

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(['GET'])
def gainIntroduction(request):
    ''' 获取公司简介信息 '''

    response = {
        'status': 'ERROR',
        'errorMessage': None,
        'introduction': None,
    }
    try:
        stock_code = request.GET.get('stockCode')
        introduction = pro.stock_company(ts_code=stock_code, fields='ts_code,introduction')["introduction"][0]
        response['status'], response['introduction'] = 'SUCCESS', introduction

    except json.JSONDecodeError:
        response['errorMessage'] = "无效的JSON负载"
        return JsonResponse(response)
    except Exception as e:
        response['errorMessage'] = str(e)
        return JsonResponse(response)

    return JsonResponse(response)