from django.apps import AppConfig
import os

class StockForecastsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stock_analyse"
    _initialized = False

    def ready(self):
        # 确保只运行一次
        if not self._initialized:
            self._initialized = True

        '''
        transformer_forecasts的model中会一直保存模型参数
        需要在每次开启项目时候清空一次
        '''
        model_dir = os.path.join(os.path.dirname(__file__), 'transformer_forecasts', 'model')

        if os.path.exists(model_dir):
            for filename in os.listdir(model_dir):
                file_path = os.path.join(model_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        os.rmdir(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')