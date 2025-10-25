"""
URL configuration for utpad_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import include, path
from django.urls import re_path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core import admin
from . import settings

# TODO: Handle routes in a combined way instead of constructing individually at each app

schema_view = get_schema_view(
    openapi.Info(
        title="Utpad Team Management API",
        default_version='v1',
        description="Utpad Team Management API",
        terms_of_service="https://github.com/manianvss/utpad?tab=BSD-3-Clause-1-ov-file#readme",
        contact=openapi.Contact(email="manianvss@hotmail.com"),
        license=openapi.License(name="BSD-3-Clause license"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

# noinspection PyUnresolvedReferences
urlpatterns = [
    # Admin plugins and other libraries
    path('admin/', include('massadmin.urls')),
    path('admin/', admin.site.urls),
    # For Advanced filters path('advanced_filters/', include('advanced_filters.urls')),

    # Modules
    path('api/', include('core.urls')),
    path('execution/', include('execution.urls')),
    path('capacity/', include('capacity.urls')),

    # Swagger
    # path('swagger/', schema_view, name='docs'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Trap code access (?(py|sh|bat|htaccess))
    re_path('(^.*[.](py|sh|bat|htaccess)$)',
            TemplateView.as_view(template_name='errors/forbidden.html')),

    re_path(
        '(^(?!(data|admin|swagger|api|execution|capacity)).*$)',
        TemplateView.as_view(template_name='index.html')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

for STATIC_URL in settings.STATIC_URLS:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
