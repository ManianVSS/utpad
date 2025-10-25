from core.views import default_search_fields, default_ordering, id_fields_filter_lookups, fk_fields_filter_lookups, \
    string_fields_filter_lookups, compare_fields_filter_lookups, date_fields_filter_lookups, \
    exact_fields_filter_lookups, ServerOrgGroupObjectLevelPermission, ServerOrgGroupViewSet, \
    datetime_fields_filter_lookups, org_model_view_set_filterset_fields, org_model_ordering_fields
from .models import Attachment, Tag, ProgramIncrement, Epic, Feature, Sprint, Story, Feedback
from .serializers import ExecutionAttachmentSerializer, ExecutionTagSerializer, ProgramIncrementSerializer, \
    EpicSerializer, \
    ExecutionFeatureSerializer, \
    SprintSerializer, StorySerializer, FeedbackSerializer


class ExecutionAttachmentViewSet(ServerOrgGroupViewSet):
    queryset = Attachment.objects.all()
    serializer_class = ExecutionAttachmentSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class ExecutionTagViewSet(ServerOrgGroupViewSet):
    queryset = Tag.objects.all()
    serializer_class = ExecutionTagSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'summary', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'description': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class ProgramIncrementViewSet(ServerOrgGroupViewSet):
    queryset = ProgramIncrement.objects.all()
    serializer_class = ProgramIncrementSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'summary', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class EpicViewSet(ServerOrgGroupViewSet):
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'summary', 'weight', 'pi', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'weight': compare_fields_filter_lookups,
        'pi': fk_fields_filter_lookups,
        'pi__name': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class ExecutionFeatureViewSet(ServerOrgGroupViewSet):
    queryset = Feature.objects.all()
    serializer_class = ExecutionFeatureSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'summary', 'weight', 'epic', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'weight': compare_fields_filter_lookups,
        'epic': fk_fields_filter_lookups,
        'epic__name': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class SprintViewSet(ServerOrgGroupViewSet):
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'pi', 'start_date', 'end_date', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'pi': fk_fields_filter_lookups,
        'pi__name': string_fields_filter_lookups,
        'start_date': date_fields_filter_lookups,
        'end_date': date_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class StoryViewSet(ServerOrgGroupViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'summary', 'weight', 'rank', 'sprint', 'feature', ] + org_model_ordering_fields
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'weight': compare_fields_filter_lookups,
        'rank': compare_fields_filter_lookups,
        'sprint': fk_fields_filter_lookups,
        'sprint__name': string_fields_filter_lookups,
        'feature': fk_fields_filter_lookups,
        'feature__name': string_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)


class FeedbackViewSet(ServerOrgGroupViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [ServerOrgGroupObjectLevelPermission]
    search_fields = default_search_fields
    ordering_fields = ['name', 'summary', 'description', 'pi', ]
    ordering = default_ordering
    filterset_fields = {
        'name': string_fields_filter_lookups,
        'summary': string_fields_filter_lookups,
        'description': string_fields_filter_lookups,
        'pi': fk_fields_filter_lookups,
    }.update(org_model_view_set_filterset_fields)
