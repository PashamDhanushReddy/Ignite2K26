from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', RedirectView.as_view(url='https://ignite2k27-admin.onrender.com/', permanent=False)),
    path('admin', RedirectView.as_view(url='https://ignite2k27-admin.onrender.com/', permanent=False)),
    path('django-admin/', admin.site.urls),
    path('', include('web.urls')),
]
