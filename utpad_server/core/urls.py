from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from .apiviews import get_user_profile_details, ExportZIPDataView, ImportZIPDataView, export_all_data_as_excel
from .views import UserViewSet, GroupViewSet, AttachmentViewSet, OrgGroupViewSet, ConfigurationViewSet, SiteViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

router.register(r'configuration', ConfigurationViewSet)
router.register(r'org_groups', OrgGroupViewSet)

router.register(r'attachments', AttachmentViewSet)
router.register(r'sites', SiteViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),

    path('auth/restframework', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/jwt/login', jwt_views.TokenObtainPairView.as_view()),
    path('auth/jwt/refresh', jwt_views.TokenRefreshView.as_view()),

    path('get_user_profile', get_user_profile_details),
    path('export/zip', ExportZIPDataView.as_view()),
    path('import/zip', ImportZIPDataView.as_view()),
    path('export/excel', export_all_data_as_excel),
]
