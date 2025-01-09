from . import manage_views
from django.urls import path

urlpatterns = [
    path("deleteUser/", manage_views.deleteUser, name="delete_user"),
    path("editUserBalance/", manage_views.editUserBalance, name="edit_user_balance"),
    path("queryUsers/", manage_views.queryUsers, name="query_users"),
]
