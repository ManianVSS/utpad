from django.contrib.auth.models import User, Group
from django.core.exceptions import FieldDoesNotExist
from rest_framework import viewsets
from rest_framework.permissions import DjangoObjectPermissions, DjangoModelPermissions, IsAdminUser, BasePermission
from rest_framework.viewsets import ModelViewSet

from .models import Attachment, OrgGroup, Configuration, Site
from .serializers import UserSerializer, GroupSerializer, AttachmentSerializer, OrgGroupSerializer, \
    ConfigurationSerializer, SiteSerializer

exact_fields_filter_lookups = ['exact', ]
# many_to_many_id_field_lookups = ['contains']
id_fields_filter_lookups = ['exact', 'in', ]
enum_fields_filter_lookups = id_fields_filter_lookups
fk_fields_filter_lookups = ['exact', 'in', 'isnull']
string_fields_filter_lookups = ['exact', 'iexact', 'icontains', 'regex', ]
# 'startswith', 'endswith', 'istartswith','iendswith', 'contains',
compare_fields_filter_lookups = ['exact', 'lte', 'lt', 'gt', 'gte', ]
date_fields_filter_lookups = ['exact', 'lte', 'gte', 'range', ]
# date,year, month, day, week, week_day, iso_week, iso_week_day, quarter
datetime_fields_filter_lookups = ['exact', 'lte', 'gte', 'range', ]
# time, hour, minute, second
default_search_fields = ['name', 'summary', 'description', ]
default_ordering = ['id', ]


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class DjangoObjectPermissionsOrAnonReadOnly(DjangoObjectPermissions):
    """
    Similar to DjangoObjectPermissions, except that anonymous users are
    allowed read-only access.
    """
    authenticated_users_only = False


class ServerOrgGroupViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        if (user is None) or user.is_superuser:
            return super().get_queryset()

        model = self.queryset.model

        if (self.action == 'list') and hasattr(model, 'get_list_query_set'):
            return model.get_list_query_set(model, self.request.user)
        else:
            return super().get_queryset()


class ServerOrgGroupObjectLevelPermission(DjangoModelPermissions):
    # authenticated_users_only = False

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        # If request is read only, allow as the queryset will be filtered by model's get_list_query_set
        if request.method in ('HEAD', 'OPTIONS', 'GET'):
            return True

        base_permission = super().has_permission(request, view)

        match request.method:
            case 'HEAD' | 'OPTIONS' | 'GET':
                return request.user.has_perm('core.tool_integration_read') or base_permission
            case 'POST' | 'PUT' | "PATCH":
                return request.user.has_perm('core.tool_integration_write') or base_permission
            case 'DELETE':
                return request.user.has_perm('core.tool_integration_delete') or base_permission
            case _:
                return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if (user is None) or user.is_superuser:
            return super().has_object_permission(request, view, obj)

        is_anonymous_request = not request.user or not request.user.is_authenticated or request.user.is_anonymous

        # User needs to have base permission if not super-user
        base_permission = super().has_permission(request, view) and super().has_object_permission(request, view, obj)

        queryset = self._queryset(view)
        model_cls = queryset.model

        try:
            match request.method:
                case 'HEAD' | 'OPTIONS':
                    return request.user.has_perm('core.tool_integration_read') or base_permission
                case 'POST':
                    return request.user.has_perm('core.tool_integration_write') or base_permission
                case 'GET':
                    # For anonymous requests, only allow if model's can_read allows it
                    if is_anonymous_request:
                        return hasattr(model_cls, 'can_read') and model_cls.can_read(obj, request.user)

                    return request.user.has_perm('core.tool_integration_read') or (base_permission and (
                            not hasattr(model_cls, 'can_read') or model_cls.can_read(obj, request.user)))
                case 'PUT' | "PATCH":
                    return request.user.has_perm('core.tool_integration_write') or (base_permission and (
                            not hasattr(model_cls, 'can_modify') or model_cls.can_read(obj, request.user)))
                case 'DELETE':
                    return request.user.has_perm('core.tool_integration_delete') or (base_permission and (
                            not hasattr(model_cls, 'can_delete') or model_cls.can_delete(obj, request.user)))
                case _:
                    return False
        except FieldDoesNotExist:
            return False


class ToolIntegrationReadPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.has_perm('core.tool_integration_read')


class ToolIntegrationWritePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.has_perm('core.tool_integration_write')


class ToolIntegrationDeletePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.has_perm('core.tool_integration_delete')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]
    search_fields = [
        'id', 'id',
        'username',
        'first_name',
        'last_name',
        'email'
    ]
    ordering_fields = [
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
    ]
    ordering = default_ordering
    filterset_fields = {
        # Fields available in django.contrib.auth.models.User
        'id': id_fields_filter_lookups,
        'username': string_fields_filter_lookups,
        'first_name': string_fields_filter_lookups,
        'last_name': string_fields_filter_lookups,
        'email': string_fields_filter_lookups,
        'is_staff': exact_fields_filter_lookups,
        'is_active': exact_fields_filter_lookups,
        'date_joined': date_fields_filter_lookups,
        'last_login': date_fields_filter_lookups,
        'is_superuser': exact_fields_filter_lookups,
        'groups': fk_fields_filter_lookups,
        'user_permissions': fk_fields_filter_lookups,
    }


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsSuperUser]
    search_fields = [
        'id',
        'name',
        'permissions__name',
    ]

    ordering_fields = [
        'id',
        'name', ]
    ordering = default_ordering
    filterset_fields = {
        # Fields available in django.contrib.auth.models.Group
        'id': id_fields_filter_lookups,
        'name': string_fields_filter_lookups,
        'permissions': fk_fields_filter_lookups,
    }


base_model_view_set_filterset_fields = {
    # Fields from BaseModel
    'id': id_fields_filter_lookups,

    'created_at': datetime_fields_filter_lookups,
    'updated_at': datetime_fields_filter_lookups,
    'published': exact_fields_filter_lookups,
    'is_public': exact_fields_filter_lookups,
}
base_model_ordering_fields = [
    'id',
    'created_at',
    'updated_at',
    'published',
    'is_public',
]


# filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

class ConfigurationViewSet(ModelViewSet):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name', 'value', 'description', ]
    ordering_fields = base_model_ordering_fields + ['name', ]
    ordering = ['name', 'updated_at']
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'value': string_fields_filter_lookups,
    }.update(base_model_view_set_filterset_fields)


class OrgGroupViewSet(ServerOrgGroupViewSet):
    queryset = OrgGroup.objects.all()
    serializer_class = OrgGroupSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = base_model_ordering_fields + ['name', 'auth_group', 'org_group', 'leaders', ]
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'auth_group': fk_fields_filter_lookups,
        'org_group': fk_fields_filter_lookups,
        'leaders': exact_fields_filter_lookups,
        'members': exact_fields_filter_lookups,
        'guests': exact_fields_filter_lookups,
        'consumers': exact_fields_filter_lookups,
    }.update(base_model_view_set_filterset_fields)


org_model_view_set_filterset_fields = {
    # Fields from OrgModel
    'id': id_fields_filter_lookups,

    'created_at': datetime_fields_filter_lookups,
    'updated_at': datetime_fields_filter_lookups,
    'published': exact_fields_filter_lookups,
    'is_public': exact_fields_filter_lookups,

    'org_group': fk_fields_filter_lookups,
}

org_model_ordering_fields = [
    'id',
    'created_at',
    'updated_at',
    'published',
    'is_public',
    'org_group',
]


class AttachmentViewSet(ServerOrgGroupViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class SiteViewSet(ServerOrgGroupViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)
