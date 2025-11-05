"""
Main URL configuration for Farmetrics project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/farmers/', include('apps.farmers.urls')),
    path('api/v1/farms/', include('apps.farms.urls')),
    path('api/v1/regions/', include('apps.regions.urls')),
    path('api/v1/visits/', include('apps.visits.urls')),
    path('api/v1/media/', include('apps.media.urls')),
    path('api/v1/requests/', include('apps.requests.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/core/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Farmetrics Administration"
admin.site.site_title = "Farmetrics Admin"
admin.site.index_title = "Welcome to Farmetrics Administration"

