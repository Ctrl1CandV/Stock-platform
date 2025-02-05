from django.urls import path
from . import views

urlpatterns = [
    path("forecastStock/", views.forecastStock, name="forecast_stock"),
    path("showZScore/", views.showZScore, name="show_z_score"),
    path("showSharpeRatio/", views.showSharpeRatio, name="show_sharpe_ratio"),
]