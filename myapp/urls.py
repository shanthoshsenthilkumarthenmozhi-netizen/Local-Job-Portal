from django.urls import path, include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.index, name='home'),
    path('admin_dashboard/', include('admin_dashboard.urls')),
    path('companies/', include('companies.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
