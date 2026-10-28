from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('my-sales/', views.my_sales, name='my_sales'),
    path('pos/', views.pos_terminal, name='pos'),
    path('create-sale/', views.create_sale, name='create_sale'),
    path('export-csv/', views.export_sales_csv, name='export_sales_csv'),
    path('<int:sale_id>/', views.sale_detail, name='sale_detail'),

]