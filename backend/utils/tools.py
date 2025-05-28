import chinese_calendar as calendar
from dotenv import load_dotenv
import datetime, time
import random, string
import tushare as ts
import re, os

from .response_view import APIException
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

load_dotenv()
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
if not TUSHARE_TOKEN:
    raise ValueError("TUSHARE_TOKEN not found in environment variables.")
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api(TUSHARE_TOKEN)

def validatePasswordComplexity(user_password: str):
    if len(user_password) < 8 or len(user_password) > 15:
        raise APIException("密码长度必须在8-15位之间")

    if not any(char.isdigit() for char in user_password):
        raise APIException("密码必须包含至少一个数字")
    
    if not any(char.isalpha() for char in user_password):
        raise APIException("密码必须包含至少一个字母")

    allowed_pattern = r'^[a-zA-Z0-9_*!]+$'
    if not re.match(allowed_pattern, user_password):
        raise APIException("密码只能包含字母、数字和'_'、'*'、'!'特殊字符")

def tradable():
    # 测试模式不检查是否能够交易
    if os.getenv("RUN_MODE") == "TEST":
        return True

    now = timezone.now().time()
    is_trading_time = ((datetime.time(9, 30) <= now <= datetime.time(11, 30)) or
                        (datetime.time(13, 0) <= now <= datetime.time(15, 0)))
    
    if is_trading_time:
        today = timezone.now().strftime("%Y%m%d")
        trading = pro.trade_cal(exchange='', start_date=today, end_date=today)['is_open'][0]
        return bool(trading)
    else:
        return False

# 寻找最近工作日
def get_previous_workday():
    previous_day = timezone.now().date() - datetime.timedelta(days=1)
    while not calendar.is_workday(previous_day):
        previous_day -= datetime.timedelta(days=1)
    return previous_day.strftime('%Y%m%d')

def generate_verification_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def send_verification_code_code(to_email: str) -> int:
    verification_code = generate_verification_code()
    email_from, email_title = settings.EMAIL_FROM, settings.EMAIL_TITLE
    email_body = f"您在模拟证券交易平台的邮箱注册验证码为：{verification_code}, 该验证码有效时间为两分钟，请及时进行验证。"
    status = send_mail(email_title, email_body, email_from, [to_email])
    return status, verification_code