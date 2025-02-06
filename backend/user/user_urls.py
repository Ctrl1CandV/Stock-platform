from . import user_views
from django.urls import path

urlpatterns = [
    path("register", user_views.register, name='register'),
    path("login", user_views.login, name='user_login'),
    path("gainUserInformation", user_views.gainUserInformation, name='gain_user_information'),
    path("updateProfile", user_views.updateProfile, name='update_profile'),
    path("updateBalance", user_views.updateBalance, name='update_balance'),
    path("changePassword", user_views.changePassword, name='change_password'),
    path("getStockOwnership", user_views.getStockOwnership, name='get_stock_ownership'),
    path("getTransactionRecords", user_views.getTransactionRecords, name='get_transaction_records'),
]
