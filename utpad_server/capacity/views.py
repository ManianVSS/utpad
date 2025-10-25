from rest_framework import permissions

from core.views import default_search_fields, default_ordering, id_fields_filter_lookups, fk_fields_filter_lookups, \
    string_fields_filter_lookups, exact_fields_filter_lookups, compare_fields_filter_lookups, \
    date_fields_filter_lookups, ServerOrgGroupObjectLevelPermission, ServerOrgGroupViewSet, \
    datetime_fields_filter_lookups, enum_fields_filter_lookups, org_model_view_set_filterset_fields, \
    base_model_view_set_filterset_fields, org_model_ordering_fields, base_model_ordering_fields
from .models import Attachment, Engineer, SiteHoliday, Leave, EngineerOrgGroupParticipation
from .serializers import CapacityAttachmentSerializer, EngineerSerializer, SiteHolidaySerializer, LeaveSerializer, \
    EngineerOrgGroupParticipationSerializer


class CapacityAttachmentViewSet(ServerOrgGroupViewSet):
    queryset = Attachment.objects.all()
    serializer_class = CapacityAttachmentSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class EngineerViewSet(ServerOrgGroupViewSet):
    queryset = Engineer.objects.all()
    serializer_class = EngineerSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['employee_id', 'name', 'auth_user', 'role', 'site', 'points', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'employee_id': exact_fields_filter_lookups,
        'name': exact_fields_filter_lookups,
        'auth_user': fk_fields_filter_lookups,
        'role': exact_fields_filter_lookups,
        'site': fk_fields_filter_lookups,
        'points': compare_fields_filter_lookups,
        'auth_user__username': exact_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class EngineerOrgGroupParticipationViewSet(ServerOrgGroupViewSet):
    queryset = EngineerOrgGroupParticipation.objects.all()
    serializer_class = EngineerOrgGroupParticipationSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['engineer', 'role', 'capacity', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'engineer': fk_fields_filter_lookups,
        'org_group': fk_fields_filter_lookups,
        'role': string_fields_filter_lookups,
        'capacity': compare_fields_filter_lookups,
    }.update(base_model_view_set_filterset_fields)


class SiteHolidayViewSet(ServerOrgGroupViewSet):
    queryset = SiteHoliday.objects.all()
    serializer_class = SiteHolidaySerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'date', 'site', ] + base_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'date': date_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'site': fk_fields_filter_lookups,
    }.update(base_model_view_set_filterset_fields)


class LeaveViewSet(ServerOrgGroupViewSet):
    queryset = Leave.objects.filter(published=True)
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoObjectPermissions]
    search_fields = default_search_fields
    ordering_fields = ['engineer', 'start_date', 'end_date', 'status', ] + base_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'engineer': fk_fields_filter_lookups,
        'start_date': date_fields_filter_lookups,
        'end_date': date_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'status': enum_fields_filter_lookups,
    }.update(base_model_view_set_filterset_fields)
