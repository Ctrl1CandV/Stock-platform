from django.apps import AppConfig
import sys

class StockPlatformConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "platform_functions"
    _initialized = False

    def ready(self):
        # 确保只运行一次
        if not self._initialized:
            self._initialized = True

        '''
        stock_basic_views.py中调用了models的内容
        如果不写在ready中会导致循环调用的错误
        '''
        if 'runserver' in sys.argv:
            from .stock_basic_views import updateStockBasic
            updateStockBasic()