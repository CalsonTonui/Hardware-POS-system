
from django.urls import path

from . import views


urlpatterns = [

    # Supplier list
    path(
        '',
        views.supplier_list,
        name='supplier_list'
    ),

    # Add supplier
    path(
        'add/',
        views.supplier_create,
        name='supplier_add'
    ),

    # Supplier details
    path(
        '<int:pk>/',
        views.supplier_detail,
        name='supplier_detail'
    ),

    # Edit supplier
    path(
        '<int:pk>/edit/',
        views.supplier_update,
        name='supplier_edit'
    ),

    # Delete supplier
    path(
        '<int:pk>/delete/',
        views.supplier_delete,
        name='supplier_delete'
    ),

]

