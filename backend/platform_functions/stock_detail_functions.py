from dateutil.relativedelta import relativedelta
from typing import Tuple, Dict, List
from .tushare_client import ts, pro
from django.utils import timezone
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas_ta as ta
import pandas as pd
import datetime
import base64
import io

import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings("ignore")

def plot_technical_indicator(data, indicator_name, title, color='blue'):
    """
    绘制技术指标图表并返回 Base64 编码
    data: 包含技术指标的 DataFrame
    indicator_name: 技术指标列名
    title: 图表标题
    color: 线条颜色
    """
    plt.figure(figsize=(12, 6))
    plt.plot(data[indicator_name], color=color)
    plt.title(title)
    plt.legend()

    # 将图像保存为 Base64 编码
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return image_base64

def technical_indicator_charts(stock_code, data: pd.DataFrame = None):
    # 获取数据
    if data is None:
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=400)
        start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
        data = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        data = data[['trade_date', 'high', 'low', 'close']]

    # 计算指标并展示图表
    indicators = calculate_technical_indicators(data)
    charts = {
        'MACDImage': 'data:image/png;base64,' + plot_technical_indicator(indicators, 'MACD_12_26_9', 'MACD'),
        'KDJImage': 'data:image/png;base64,' + plot_technical_indicator(indicators, 'K_9_3', 'KDJ (K Line)'),
        'BOLLImage': 'data:image/png;base64,' + plot_technical_indicator(indicators, 'BBM_5_2.0', 'BOLL (Middle Band)'),
        'BIASImage': 'data:image/png;base64,' + plot_technical_indicator(indicators, 'BIAS_SMA_26', 'BIAS'),
        'RSIImage': 'data:image/png;base64,' + plot_technical_indicator(indicators, 'RSI_14', 'RSI'),
        'WRImage': 'data:image/png;base64,' + plot_technical_indicator(indicators, 'WILLR_14', 'WR'),
    }
    return charts

def valuation_ratio_charts(stock_code):
    # 获取数据并按照交易日期排序
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=400)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    basic_stable = pro.daily_basic(
        ts_code=stock_code, fields='trade_date,pe,pb,ps',
        start_date=start_date, end_date=end_date,
    )
    basic_stable['trade_date'] = pd.to_datetime(basic_stable['trade_date'])
    basic_stable.set_index('trade_date', inplace=True)
    basic_stable = basic_stable.sort_index(ascending=True)

    # 绘制图表
    plt.figure(figsize=(16, 8))
    plt.plot(basic_stable.index, basic_stable['pe'], label='PE', color='blue')
    plt.plot(basic_stable.index, basic_stable['pb'], label='PB', color='green')
    plt.plot(basic_stable.index, basic_stable['ps'], label='PS', color='red')
    plt.title(f'{stock_code}', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Rate', fontsize=12)
    plt.legend()
    plt.gcf().autofmt_xdate()

    # 将图像保存为 Base64 编码
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return image_base64

def financial_metric_form(stock_code):
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=400)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    indicator_data = pro.fina_indicator(
        ts_code=stock_code, start_date=start_date, end_date=end_date,
        fields='ann_date,profit_dedt,q_profit_yoy,or_yoy,bps,cfps,roe,ar_turn,grossprofit_margin'
    )
    income_data = pro.income(
        ts_code=stock_code, start_date=start_date, end_date=end_date,
        fields='ann_date,revenue,n_income_attr_p,sell_exp,admin_exp,rd_exp,fin_exp,basic_eps'
    )
    merged_data = pd.merge(indicator_data, income_data, on='ann_date', how='inner')
    return merged_data.to_dict(orient='records')

def get_stock_data(stock_code: str, time_span: int, type: int) -> Tuple[List[Dict], str]:
    """
    获取股票数据但不生成图表，直接返回处理后的数据
    """
    end_date = timezone.now().date()
    if type == 1:
        start_date = end_date - datetime.timedelta(days=time_span)
        data = pro.daily(ts_code=stock_code, start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
        title = f"{stock_code} Daily candlestick chart"
    elif type == 2:
        start_date = end_date - datetime.timedelta(days=7 * time_span)
        data = pro.weekly(ts_code=stock_code, start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
        title = f"{stock_code} Weekly candlestick chart"
    elif type == 3:
        start_date = end_date - relativedelta(months=time_span)
        data = pro.monthly(ts_code=stock_code, start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
        title = f"{stock_code} Monthly candlestick chart"
    else:
        raise ValueError("Invalid chart type")
    
    # 处理数据格式
    processed_data = data[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']].copy()
    processed_data['trade_date'] = processed_data['trade_date'].astype(str)
    
    # 转换为字典列表
    return processed_data.to_dict(orient='records'), title

def calculate_technical_indicators(data):
    ''' 计算技术指标，输入为包含trade_date,high,low,close的 DataFrame '''
    data['trade_date'] = pd.to_datetime(data['trade_date'])
    data.set_index('trade_date', inplace=True)
    data = data.sort_index(ascending=True)

    # 计算各种指标:MACD、KDJ、BOLL、BIAS、RSI和WR
    data.ta.macd(append=True)
    data.ta.kdj(append=True)
    data.ta.bbands(append=True)
    data.ta.bias(append=True)
    data.ta.rsi(append=True)
    data.ta.willr(append=True)

    return data

def technical_indicator_data(stock_code, data: pd.DataFrame = None):
    # 获取数据
    if data is None:
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=400)
        start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
        data = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        data = data[['trade_date', 'high', 'low', 'close']]

    # 计算指标，删除所有技术指标全为0的行
    indicators = calculate_technical_indicators(data)
    indicators = indicators[~(indicators[['MACD_12_26_9', 'K_9_3', 'BBM_5_2.0', 'BIAS_SMA_26', 'RSI_14', 'WILLR_14']] == 0).all(axis=1)]
    indicators = indicators[['MACD_12_26_9', 'K_9_3', 'BBM_5_2.0', 'BIAS_SMA_26', 'RSI_14', 'WILLR_14']]
    return indicators.to_dict(orient='records')

def valuation_ratio_charts(stock_code):
    # 获取数据并按照交易日期排序
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=400)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    basic_stable = pro.daily_basic(
        ts_code=stock_code, fields='trade_date,pe,pb,ps',
        start_date=start_date, end_date=end_date,
    )
    basic_stable['trade_date'] = pd.to_datetime(basic_stable['trade_date'])
    basic_stable.set_index('trade_date', inplace=True)
    basic_stable = basic_stable.sort_index(ascending=True)

    return basic_stable.to_dict(orient='records')

if __name__ == '__main__':
    stock_code = '002236.SZ'
    # print(financial_metric_form(stock_code))
    print(technical_indicator_charts(stock_code))