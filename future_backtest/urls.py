from django.urls import path

from future_backtest import views

app_name = 'future_backtest'

urlpatterns = [
    path('', views.BacktestView.as_view(), name='backtest'),
]
