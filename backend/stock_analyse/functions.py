from .transformer_forecasts import forecasts_functions
from platform_functions.tushare_client import ts, pro
import chinese_calendar as calendar
from django.utils import timezone
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
import requests

# 寻找最近工作日
def get_previous_workday():
    previous_day = timezone.now().date() - datetime.timedelta(days=1)
    while not calendar.is_workday(previous_day):
        previous_day -= datetime.timedelta(days=1)
    return previous_day.strftime('%Y%m%d')

'''
单位测试阶段先使用Tushare直接获取
后期使用ORM获取数据库的数据进行训练和预测
'''
def forecast_result(stock_code, data):
    forecasts_data = forecasts_functions.train(stock_code, data)
    prediction = forecasts_functions.forecast(stock_code, forecasts_data)
    result = prediction[0, 0]
    pre_close = data['close'][0]
    return (result - pre_close) / pre_close * 100, result

def calculate_Zscore(stock_code):
    #  初始化参数
    end_date = timezone.now().date()
    start_date = end_date.replace(year=end_date.year - 1)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    token = '66e72ae286def4e5826d1edc84f45cdad596c34137a91396b335cefd'
    pro = ts.pro_api(token)

    # 获取模型需要的数据，以万元为单位，并统一使用一年的数据均值
    basic_stable = pro.daily_basic(
        ts_code=stock_code, start_date=start_date, end_date=end_date,
        fields='total_mv'
    )
    income_table = pro.income(
        ts_code=stock_code, start_date=start_date, end_date=end_date,
        fields='total_profit,revenue,ann_date'
    )
    balancesheet_table = pro.balancesheet(
        ts_code=stock_code, start_date=start_date, end_date=end_date,
        fields='total_cur_assets,total_cur_liab,total_ncl'
    )
    indicator_table = pro.fina_indicator(
        ts_code=stock_code, start_date=start_date, end_date=end_date,
        fields='retained_earnings,assets_turn,ann_date'
    )
    total_cur_assets, total_cur_liab, total_ncl = balancesheet_table['total_cur_assets'].mean() / 10000, \
                                                  balancesheet_table['total_cur_liab'].mean() / 10000, \
                                                  balancesheet_table['total_ncl'].mean() / 10000
    total_profit, revenue = income_table['total_profit'].mean() / 10000, income_table['revenue'].mean() / 10000
    total_mv = basic_stable['total_mv'].mean()
    finan_exp = pro.cashflow(
        ts_code=stock_code, start_date=start_date, end_date=end_date, fields='finan_exp'
    )['finan_exp'].mean() / 10000
    retained_earnings, assets_turn = indicator_table['retained_earnings'].mean() / 10000, indicator_table[
        'assets_turn'].mean()

    # 利用总资产周转率和营业收入计算总资产
    merged_data = pd.merge(income_table, indicator_table, on='ann_date', how='inner').drop_duplicates(subset='ann_date')
    total_assets = (merged_data['revenue'] / merged_data['assets_turn']).mean() / 10000

    # 计算Z分模型的最终得分
    X1 = (total_cur_assets - total_cur_liab) * 100 / total_assets
    X2 = retained_earnings * 100 / total_assets
    X3 = (total_profit + finan_exp) * 100 / total_assets
    X4 = total_mv * 100 / (total_cur_liab + total_ncl)
    X5 = revenue * 100 / total_assets
    z_score = 0.012 * X1 + 0.014 * X2 + 0.033 * X3 + 0.006 * X4 + 0.999 * X5
    return  round(z_score, 4), [X1, X2, X3, X4, X5]

def crawling_riskfree_rate():
    # 爬取数据
    url = "https://yield.chinabond.com.cn/cbweb-czb-web/czb/moreInfo?locale=cn_ZH&nameType=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到存放数据的table和对应的数据元素
    table = soup.find(id='Container').find(id='gjqxData').find('table')

    # 使用列表推导式提取第二列的所有数据
    rates = [
        columns[1].get_text().strip('%')
        for row in table.find_all('tr')
        if len(columns := row.find_all('td')) > 1
    ][2:]
    rate_date = ['6月', '1年', '2年', '3年', '5年', '7年', '10年', '30年']
    rate = dict(zip(rate_date, rates))

    return rate

def calculate_sharpe_ratio(rate, data):
    data = data / 100
    mean, std = np.mean(data), np.std(data)
    sharpe_ratio = (mean - rate) / std
    return mean, round(sharpe_ratio, 2)

if __name__ == '__main__':
    stock_code = '002558.SZ'
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=500)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    data = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)

    # 如果是ORM获取的data需要进行data = pd.DataFrame(list(data.values()))进行数据适应

    # print(forecast_result(stock_code, data))
    # rate = crawling_Riskfree_rate()
    # print(calculate_sharpe_ratio(float(rate['10年']), data['pct_chg']))