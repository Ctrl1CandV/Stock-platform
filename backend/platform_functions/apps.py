from django.core.cache import cache
from django.apps import AppConfig
import shutil
import sys
import os

from dotenv import load_dotenv
load_dotenv()

'''
由于Django项目启动重复加载的问题
以下代码始终会运行多次，无法解决
'''
def check_redis():
    try:
        cache.set('redis_status', 1, 1)
    except Exception as e:
        print("Redis连接失败", end=" ")
        sys.exit(1)
    print("Redis连接成功")

def cleanModelData():
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
    if os.path.exists(model_dir):
        try:
            # 使用 shutil.rmtree 递归删除目录及其内容
            shutil.rmtree(model_dir)
            os.makedirs(model_dir)
        except Exception as e:
            print(f'模型数据清楚失败。 原因为{e}')

class StockPlatformConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "platform_functions"
    _startup_executed = False

    def ready(self):
        if not self._startup_executed:
            _startup_executed = True
            self.on_startup()

    def on_startup(self):
        from .stock_basic_views import updateStockBasic, cleanMarket
        check_redis()
        cleanMarket()
        updateStockBasic()
        cleanModelData()
        print("MySQL连接成功，平台初始化完成")