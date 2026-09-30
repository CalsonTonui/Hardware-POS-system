from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # ADMINISTRATOR AUTHENTICATION
    # =====================================================

    path(
        'admin-login/',
        views.AdminLoginView.as_view(),
        name='admin_login'
    ),

    # =====================================================
    # ADMINISTRATOR DASHBOARD
    # =====================================================

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # =====================================================
    # USER MANAGEMENT
    # =====================================================

    path(
        'users/',
        views.user_list,
        name='user_list'
    ),

    path(
        'users/add/',
        views.user_add,
        name='user_add'
    ),

    path(
        'users/<int:user_id>/edit/',
        views.user_edit,
        name='user_edit'
    ),

    path(
        'users/<int:user_id>/toggle-status/',
        views.user_toggle_status,
        name='user_toggle_status'
    ),

    path(
        'users/<int:user_id>/delete/',
        views.user_delete,
        name='user_delete'
    ),
]