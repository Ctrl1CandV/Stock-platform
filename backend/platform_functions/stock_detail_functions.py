from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas_ta as ta
import tushare as ts
import pandas as pd
import datetime
import base64
import io

import warnings
warnings.filterwarnings("ignore")

# 初始化参数
token = '66e72ae286def4e5826d1edc84f45cdad596c34137a91396b335cefd'
pro = ts.pro_api(token)

def draw_market_chart(data, title):
    # 数据的处理和格式转化
    data = data[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']]
    data['trade_date'] = pd.to_datetime(data['trade_date'], format='%Y%m%d')
    data.set_index('trade_date', inplace=True)
    ohlc_data = data[['open', 'high', 'low', 'close']].copy()
    ohlc_data['volume'] = data['vol']

    # 自定义表格样式
    market_color = mpf.make_marketcolors(up='green', down='red', inherit=True)
    style = mpf.make_mpf_style(base_mpf_style='charles',marketcolors=market_color,
            gridcolor='lightgray',gridstyle='-',y_on_right=False)

    # 将图像以字节流形式保存到内存中
    buffer = io.BytesIO()
    mpf.plot(
        ohlc_data,
        type='candle',
        volume=True,
        style=style,
        figsize=(14, 8),
        title=title,
        ylabel='Price',
        ylabel_lower='Volum',
        mav=[5, 10, 20],
        figratio=(16, 10),
        figscale=1.3,
        tight_layout=True,
        xrotation=45,
        panel_ratios=(3, 1),
        savefig=dict(fname=buffer, format='png', bbox_inches='tight'),
    )
    buffer.seek(0)

    # 转化为Base64编码
    image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return image

def get_stock_chart(stock_code, time_span, type):
    end_date = datetime.date.today()
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
    return draw_market_chart(data, title)

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

def technical_indicator_charts(stock_code):
    # 获取数据
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=400)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    data = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
    data = data[['trade_date', 'high', 'low', 'close']]

    # 计算指标并展示图表
    indicators = calculate_technical_indicators(data)
    charts = {
        'MACDImage': plot_technical_indicator(indicators, 'MACD_12_26_9', 'MACD'),
        'KDJImage': plot_technical_indicator(indicators, 'K_9_3', 'KDJ (K Line)'),
        'BOLLImage': plot_technical_indicator(indicators, 'BBM_5_2.0', 'BOLL (Middle Band)'),
        'BIASImage': plot_technical_indicator(indicators, 'BIAS_SMA_26', 'BIAS'),
        'RSIImage': plot_technical_indicator(indicators, 'RSI_14', 'RSI'),
        'WRImage': plot_technical_indicator(indicators, 'WILLR_14', 'WR'),
    }
    return charts

def valuation_ratio_charts(stock_code):
    # 获取数据并按照交易日期排序
    end_date = datetime.date.today()
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
    financial_metric_dict = {
        'ann_date': '公告日期',
        'profit_dedt': '扣非净利润(元)',
        'q_profit_yoy': ' 净利润同比增长率(%)(单季度)',
        'or_yoy': '营业收入同比增长率(%)',
        'bps': '每股净资产(元)',
        'cfps': '每股现金流量净额(元)',
        'roe': '净资产收益率(%)',
        'ar_turn': '应收账款周转率(%)',
        'grossprofit_margin': '销售毛利率(%)',
        'revenue': '营业收入(元)',
        'n_income_attr_p': ' 净利润(不含少数股东损益)(元)',
        'basic_eps': ' 基本每股收益(元)',
        'sell_exp': '销售费用(元)',
        'admin_exp': '管理费用(元)',
        'rd_exp': '研发费用(元)',
        'fin_exp': '财务费用(元)',
    }

    end_date = datetime.date.today()
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
    merged_data = merged_data.rename(columns=financial_metric_dict)
    return merged_data.to_dict(orient='list')