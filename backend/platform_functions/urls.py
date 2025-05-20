from . import stock_basic_views, stock_detail_views
from django.urls import path, include

urlpatterns = [
    path("getCSRF", stock_basic_views.getCSRF, name="get_csrf"),
    path("isTrading", stock_basic_views.isTrading, name="is_trading"),
    path("queryStockByName", stock_basic_views.queryStockByName, name="query_stock_by_name"),
    path("queryStockByCode", stock_basic_views.queryStockByCode, name="query_stock_by_code"),
    path("buyStock", stock_basic_views.buyStock, name="buy_stock"),
    path("sellStock", stock_basic_views.sellStock, name="sell_stock"),
    path("addFavoriteStock", stock_basic_views.addFavoriteStock, name="add_favorite_stock"),
    path("removeFavoriteStock", stock_basic_views.removeFavoriteStock, name="remove_favorite_stock"),
    path("loadHomePageData", stock_basic_views.loadHomePageData, name="load_home_page_data"),
    path("updateAnnualDailyQuotes", stock_detail_views.updateAnnualDailyQuotes, name="update_annual_daily_quotes"),
    path("showStockQurve", stock_detail_views.showStockQurve, name="show_stock_qurve"),
    path("showValuationRatio", stock_detail_views.showValuationRatio, name="show_valuation_ratio"),
    path("showTechnicalIndicator", stock_detail_views.showTechnicalIndicator, name="show_technical_indicator"),
    path("getFinancialMetric", stock_detail_views.getFinancialMetric, name="get_financial_metric"),
    path("gainIntroduction", stock_detail_views.gainIntroduction, name="gain_introduction"),
    path("analyse/", include("stock_analyse.urls")),
]