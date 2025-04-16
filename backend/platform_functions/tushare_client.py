from dotenv import load_dotenv
import tushare as ts
import os

load_dotenv()

TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
if not TUSHARE_TOKEN:
    raise ValueError("TUSHARE_TOKEN not found in environment variables.")

ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api(TUSHARE_TOKEN)