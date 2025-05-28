from .models import user_accounts, manager
import json

from utils.response_view import api_view, APIException
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
'''
管理员仅有三个针对用户的基础功能
POST会改变数据，GET不会
'''
@api_view(methods=['POST'], require_token=False)
def login(request, params):
    ''' 管理员登录 '''
    manager_name, manager_password = params.get('userAccount'), params.get('password')
    try:
        Manager = manager.objects.get(manager_name=manager_name)
    except ObjectDoesNotExist:
        raise APIException("管理员不存在")
    if manager_password == Manager.manager_password:
        return { 'managerID': Manager.manager_id }
    else:
        raise APIException("密码错误")

@api_view(methods=['POST'], require_token=False)
def deleteUser(request, params):
    ''' 伪删除用户账户 '''
    user_id = params.get('userID')
    with transaction.atomic():
        user = user_accounts.objects.get(user_id=user_id)
        user.status = False
        user.save()
    return { 'userID': user_id }

@api_view(methods=['POST'], require_token=False)
def editUserBalance(request, params):
    ''' 更改用户的余额 '''
    user_id, new_balance = params.get('userID'), params.get('newBalance')
    if new_balance <=0:
        raise APIException("无效余额")

    try:
        user = user_accounts.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        raise APIException("用户不存在")
    if user.status:
        with transaction.atomic():
            user.user_balance = new_balance
            user.save()
        return { 'userID': user_id }
    else:
        raise APIException("用户账号已弃用", 403)

@api_view(methods=['GET'], require_token=False)
def queryUsers(request, params):
    ''' 查询用户账户 '''
    users = user_accounts.objects.all()
    user_list = []
    for user in users:
        user_map = {
            'userID': user.user_id,
            'userEmail': user.user_email,
            'userName': user.user_name,
            'userBalance': user.user_balance,
            'status': user.status
        }
        user_list.append(user_map)
    return { 'userList': user_list }