from platform_functions.models import manager

try:
    rootManager = manager.objects.filter(manager_name='admin')
    if not rootManager.exists():
        manager.objects.create(manager_name='admin',manager_password='admin')
except:
    print(f"数据库未准备好，可能是数据迁移尚未完成")