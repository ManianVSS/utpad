from django.contrib import admin
from django.contrib.admin.filters import RelatedOnlyFieldListFilter

from core.admin import CustomModelAdmin, org_model_list_filter_base
from .models import Attachment, Tag, ProgramIncrement, Epic, Feature, Sprint, Story, Feedback


@admin.register(Attachment)
class AttachmentAdmin(CustomModelAdmin):
    search_fields = ['name', ' file', ]
    list_filter = org_model_list_filter_base + ( )


@admin.register(Tag)
class TagAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + ( )
    search_fields = ['name', 'summary', 'description', ]


@admin.register(ProgramIncrement)
class ProgramIncrementAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + ( )
    search_fields = ['name', 'summary', 'description', ]


@admin.register(Epic)
class EpicAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'weight',
        ('pi', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'summary', 'description', ]


@admin.register(Feature)
class FeatureAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'weight',
        ('epic', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'summary', 'description', ]


@admin.register(Sprint)
class SprintAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'start_date',
        'end_date',
        ('pi', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'start_date', 'end_date', ]


@admin.register(Story)
class StoryAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'weight',
        'rank',
        ('sprint', RelatedOnlyFieldListFilter),
        ('feature', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'summary', 'description', ]


@admin.register(Feedback)
class FeedbackAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'time',
        ('pi', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'summary', 'description', ]
