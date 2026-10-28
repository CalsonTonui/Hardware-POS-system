from django.urls import path
from . import views



urlpatterns = [

    path('',views.reports_dashboard,name='reports_dashboard'),
    path('mpesa/', views.mpesa_report, name='mpesa_report'),
    path('sales-by-cashier/', views.sales_by_cashier, name='sales_by_cashier'),
    path('period/', views.period_report, name='period_report'),
    path('product-performance/', views.product_performance, name='product_performance'),
]