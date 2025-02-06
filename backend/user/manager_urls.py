from . import manager_views
from django.urls import path

urlpatterns = [
    path("login", manager_views.login, name="manager_login"),
    path("deleteUser", manager_views.deleteUser, name="delete_user"),
    path("editUserBalance", manager_views.editUserBalance, name="edit_user_balance"),
    path("queryUsers", manager_views.queryUsers, name="query_users"),
]
