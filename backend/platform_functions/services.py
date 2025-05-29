from dateutil.relativedelta import relativedelta
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas_ta as ta
import pandas as pd
import datetime
import warnings

from .models import stock_market, stock_basic
from django.utils import timezone
from django.db import transaction
from utils.tools import ts, pro
from utils.logger import logger

warnings.filterwarnings("ignore")

# 常量定义
class TimeType(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3

class MarketType(Enum):
    SHANGHAI = '1'
    SHENZHEN = '3'

# 配置常量
DEFAULT_DAYS = 400
TOP_STOCKS_COUNT = 10
NEWS_COUNT = 10
YI_UNIT = 100000000

INDEX_CODES = {
    '上证指数': '000001.SH',
    '深证成指': '399001.SZ',
    '创业板指': '399006.SZ'
}

TECHNICAL_INDICATORS = [
    'MACD_12_26_9', 'K_9_3', 'BBM_5_2.0', 
    'BIAS_SMA_26', 'RSI_14', 'WILLR_14'
]

@dataclass
class DateRange:
    """日期范围数据类"""
    start_date: str
    end_date: str
    
    @classmethod
    def from_days_ago(cls, days: int) -> 'DateRange':
        """从指定天数前创建日期范围"""
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=days)
        return cls(
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d')
        )
    
    @classmethod
    def from_months_ago(cls, months: int) -> 'DateRange':
        """从指定月数前创建日期范围"""
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=months)
        return cls(
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d')
        )

class DataProcessor:
    """数据处理工具类"""
    
    @staticmethod
    def format_amount_to_yi(amount: float) -> str:
        """将金额格式化为亿元单位"""
        return f'{amount / YI_UNIT:.2f}亿'
    
    @staticmethod
    def prepare_dataframe_for_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """为技术指标计算准备DataFrame"""
        data = data.copy()
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        data.set_index('trade_date', inplace=True)
        return data.sort_index(ascending=True)
    
    @staticmethod
    def calculate_change_percentage(current: float, previous: float) -> float:
        """计算变化百分比"""
        if previous == 0:
            return 0
        return round((current - previous) / previous * 100, 4)

class StockDataService:
    """股票数据服务类"""
    
    def get_financial_metrics(self, stock_code: str) -> List[Dict]:
        """获取财务指标数据"""
        date_range = DateRange.from_days_ago(DEFAULT_DAYS)
        
        indicator_data = pro.fina_indicator(
            ts_code=stock_code, 
            start_date=date_range.start_date, 
            end_date=date_range.end_date,
            fields='ann_date,profit_dedt,q_profit_yoy,or_yoy,bps,cfps,roe,ar_turn,grossprofit_margin'
        )
        
        income_data = pro.income(
            ts_code=stock_code, 
            start_date=date_range.start_date, 
            end_date=date_range.end_date,
            fields='ann_date,revenue,n_income_attr_p,sell_exp,admin_exp,rd_exp,fin_exp,basic_eps'
        )
        
        merged_data = pd.merge(indicator_data, income_data, on='ann_date', how='inner')
        return merged_data.to_dict(orient='records')
    
    def get_stock_data(self, stock_code: str, time_span: int, time_type: TimeType) -> Tuple[List[Dict], str]:
        """获取股票数据"""
        data_fetchers = {
            TimeType.DAILY: self._get_daily_data,
            TimeType.WEEKLY: self._get_weekly_data,
            TimeType.MONTHLY: self._get_monthly_data
        }
        
        if time_type not in data_fetchers:
            raise ValueError(f"Invalid time type: {time_type}")
        
        data, title = data_fetchers[time_type](stock_code, time_span)
        return self._process_stock_data(data), title
    
    def _get_daily_data(self, stock_code: str, time_span: int) -> Tuple[pd.DataFrame, str]:
        """获取日线数据"""
        date_range = DateRange.from_days_ago(time_span)
        data = pro.daily(
            ts_code=stock_code, 
            start_date=date_range.start_date, 
            end_date=date_range.end_date
        )
        return data, f"{stock_code} Daily candlestick chart"
    
    def _get_weekly_data(self, stock_code: str, time_span: int) -> Tuple[pd.DataFrame, str]:
        """获取周线数据"""
        date_range = DateRange.from_days_ago(7 * time_span)
        data = pro.weekly(
            ts_code=stock_code, 
            start_date=date_range.start_date, 
            end_date=date_range.end_date
        )
        return data, f"{stock_code} Weekly candlestick chart"
    
    def _get_monthly_data(self, stock_code: str, time_span: int) -> Tuple[pd.DataFrame, str]:
        """获取月线数据"""
        date_range = DateRange.from_months_ago(time_span)
        data = pro.monthly(
            ts_code=stock_code, 
            start_date=date_range.start_date, 
            end_date=date_range.end_date
        )
        return data, f"{stock_code} Monthly candlestick chart"
    
    def _process_stock_data(self, data: pd.DataFrame) -> List[Dict]:
        """处理股票数据格式"""
        processed_data = data[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']].copy()
        processed_data['trade_date'] = processed_data['trade_date'].astype(str)
        return processed_data.to_dict(orient='records')

class TechnicalIndicatorService:
    """技术指标服务类"""
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        data = DataProcessor.prepare_dataframe_for_indicators(data)
        
        # 批量计算技术指标
        indicators_methods = [
            data.ta.macd, data.ta.kdj, data.ta.bbands,
            data.ta.bias, data.ta.rsi, data.ta.willr
        ]
        
        for method in indicators_methods:
            method(append=True)
        
        return data
    
    def get_technical_indicator_data(self, stock_code: str, data: Optional[pd.DataFrame] = None) -> List[Dict]:
        """获取技术指标数据"""
        if data is None:
            data = self._fetch_stock_data_for_indicators(stock_code)
        
        indicators = self.calculate_indicators(data)
        indicators = indicators.dropna(subset=TECHNICAL_INDICATORS, how='all')
        indicators = indicators[TECHNICAL_INDICATORS].fillna(0).reset_index()
        indicators['trade_date'] = indicators['trade_date'].dt.strftime('%Y-%m-%d')
        
        return indicators.to_dict(orient='records')
    
    def _fetch_stock_data_for_indicators(self, stock_code: str) -> pd.DataFrame:
        """为技术指标获取股票数据"""
        date_range = DateRange.from_days_ago(DEFAULT_DAYS)
        data = pro.daily(
            ts_code=stock_code, 
            start_date=date_range.start_date, 
            end_date=date_range.end_date
        )
        return data[['trade_date', 'high', 'low', 'close']]

class ValuationService:
    """估值服务类"""
    
    def get_valuation_ratio_data(self, stock_code: str) -> List[Dict]:
        """获取估值比率数据"""
        date_range = DateRange.from_days_ago(DEFAULT_DAYS)
        
        basic_data = pro.daily_basic(
            ts_code=stock_code, 
            fields='trade_date,pe,pb,ps',
            start_date=date_range.start_date, 
            end_date=date_range.end_date
        )
        
        return self._process_valuation_data(basic_data)
    
    def _process_valuation_data(self, data: pd.DataFrame) -> List[Dict]:
        """处理估值数据"""
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        data.set_index('trade_date', inplace=True)
        data = data.sort_index(ascending=True)
        
        # 插值处理缺失值
        data[['pe', 'pb', 'ps']] = data[['pe', 'pb', 'ps']].interpolate(
            method='time', limit_direction='both'
        )
        
        data = data.reset_index()
        data['trade_date'] = data['trade_date'].dt.strftime('%Y-%m-%d')
        
        return data.to_dict(orient='records')

class MarketDataService:
    """市场数据服务类"""
    
    def get_top_stocks(self, trade_date: str, market_type: MarketType) -> Dict[str, str]:
        """获取十大成交股数据"""
        try:
            data = pro.hsgt_top10(trade_date=trade_date, market_type=market_type.value)
            data = data[['name', 'amount']].sort_values('amount', ascending=False)
            data['amount'] = data['amount'].apply(DataProcessor.format_amount_to_yi)
            return data.set_index('name')['amount'].to_dict()
        except Exception as e:
            logger.error(f"获取{market_type.name}十大成交股失败: {str(e)}")
            return {}
    
    def get_news_information(self) -> Dict[str, str]:
        """获取新闻信息"""
        try:
            start_time = timezone.now().strftime('%Y-%m-%d') + ' 00:00:00'
            news_data = pro.news(
                src='eastmoney', 
                start_date=start_time, 
                fields='datetime,content'
            ).head(NEWS_COUNT)
            return news_data.set_index('datetime')['content'].to_dict()
        except Exception as e:
            logger.error(f"获取新闻信息失败: {str(e)}")
            return {}
    
    def get_significant_index_changes(self, trade_date: str) -> Dict[str, float]:
        """获取重要指数变化"""
        results = {}
        for name, code in INDEX_CODES.items():
            try:
                data = pro.index_daily(ts_code=code, trade_date=trade_date)
                if not data.empty:
                    row = data.iloc[0]
                    change = DataProcessor.calculate_change_percentage(
                        row['close'], row['pre_close']
                    )
                    results[name] = change
                else:
                    results[name] = 0
            except Exception as e:
                logger.error(f"获取{name}数据失败: {str(e)}")
                results[name] = 0
        return results

class DatabaseService:
    """数据库服务类"""
    
    def clean_market_data(self) -> bool:
        """清理市场数据表"""
        try:
            with transaction.atomic():
                stock_market.objects.all().delete()
            logger.info("成功清理stock_market表")
            return True
        except Exception as e:
            logger.error(f"清除stock_market表错误: {str(e)}")
            return False
    
    def update_stock_basic_data(self) -> bool:
        """更新股票基础数据"""
        # 检查数据库连接
        if not self._check_database_ready():
            return False
        
        try:
            new_stock_data = pro.stock_basic(
                exchange='', 
                list_status='L',
                fields='ts_code, name, area, industry, list_date'
            )
            
            if new_stock_data.empty:
                logger.error("未获取到新的股票列表数据")
                return False
            
            return self._bulk_update_stock_data(new_stock_data)
            
        except Exception as e:
            logger.error(f"股票列表更新失败: {str(e)}")
            return False
    
    def _check_database_ready(self) -> bool:
        """检查数据库是否准备就绪"""
        try:
            stock_basic.objects.first()
            return True
        except Exception as db_error:
            logger.warning(
                f"数据库未准备好，可能是数据迁移尚未完成: {str(db_error)}\n"
                "请先完成数据迁移后再进行股票列表更新"
            )
            return False
    
    def _bulk_update_stock_data(self, new_data: pd.DataFrame) -> bool:
        """批量更新股票数据"""
        try:
            with transaction.atomic():
                # 清除旧数据
                stock_basic.objects.all().delete()
                
                # 批量创建新记录
                new_records = [
                    stock_basic(
                        stock_code=row['ts_code'],
                        stock_name=row['name'],
                        industry=row['industry'],
                        area=row['area'],
                        list_date=row['list_date']
                    )
                    for _, row in new_data.iterrows()
                ]
                
                stock_basic.objects.bulk_create(new_records)
                logger.info(f"成功更新{len(new_records)}条股票数据")
                return True
                
        except Exception as e:
            logger.error(f"批量更新股票数据失败: {str(e)}")
            return False

# 服务实例
stock_service = StockDataService()
technical_service = TechnicalIndicatorService()
valuation_service = ValuationService()
market_service = MarketDataService()
db_service = DatabaseService()

# 向后兼容的函数接口
def financial_metric_form(stock_code: str) -> List[Dict]:
    """获取财务指标数据"""
    return stock_service.get_financial_metrics(stock_code)

def get_stock_data(stock_code: str, time_span: int, time_type: int) -> Tuple[List[Dict], str]:
    """获取股票数据"""
    return stock_service.get_stock_data(stock_code, time_span, TimeType(time_type))

def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """计算技术指标"""
    return technical_service.calculate_indicators(data)

def technical_indicator_data(stock_code: str, data: Optional[pd.DataFrame] = None) -> List[Dict]:
    """获取技术指标数据"""
    return technical_service.get_technical_indicator_data(stock_code, data)

def valuation_ratio_data(stock_code: str) -> List[Dict]:
    """获取估值比率数据"""
    return valuation_service.get_valuation_ratio_data(stock_code)

def _get_shanghai_top10(trade_date: str) -> Dict[str, str]:
    """获取上海十大成交股数据"""
    return market_service.get_top_stocks(trade_date, MarketType.SHANGHAI)

def _get_shenzhen_top10(trade_date: str) -> Dict[str, str]:
    """获取深圳十大成交股数据"""
    return market_service.get_top_stocks(trade_date, MarketType.SHENZHEN)

def _get_news_information() -> Dict[str, str]:
    """获取新闻信息"""
    return market_service.get_news_information()

def _get_significant_index(trade_date: str) -> Dict[str, float]:
    """获取重要指数信息"""
    return market_service.get_significant_index_changes(trade_date)

def cleanMarket() -> bool:
    """清理市场数据"""
    return db_service.clean_market_data()

def updateStockBasic() -> bool:
    """更新股票基础数据"""
    return db_service.update_stock_basic_data()