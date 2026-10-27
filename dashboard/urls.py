from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/update-selection-status/', views.update_selection_status_view, name='update_selection_status'),
    path('debug/storage/', views.debug_storage_view, name='debug_storage'),
    path('debug/fields/', views.debug_fields_view, name='debug_fields'),
    path('download/<path:ppt_path>/', views.download_ppt_view, name='download_ppt'),
    path('export/', views.export_registrations_view, name='export_registrations'),
    path('logout/', views.logout_view, name='logout'),
]
