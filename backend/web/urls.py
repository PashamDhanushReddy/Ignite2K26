from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('success/', views.success, name='success'),
    path('receipt/', views.receipt, name='receipt'),
    path('pdf-receipt/', views.pdf_receipt, name='pdf_receipt'),
    path('api/gallery/', views.gallery_api, name='gallery_api'),
]
