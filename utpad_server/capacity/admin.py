from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter

from core.admin import CustomModelAdmin, org_model_list_filter_base, base_model_list_filter_base
from core.views import default_search_fields
from .models import Attachment, Engineer, SiteHoliday, Leave, EngineerOrgGroupParticipation


@admin.register(Attachment)
class AttachmentAdmin(CustomModelAdmin):
    search_fields = ['name', 'file', ]
    list_filter = org_model_list_filter_base + ( )


@admin.register(Engineer)
class EngineerAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'role',
        ('site', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'employee_id', 'role']


@admin.register(EngineerOrgGroupParticipation)
class EngineerOrgGroupParticipationAdmin(CustomModelAdmin):
    list_filter = org_model_list_filter_base + (
        'role',
        ('engineer', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'engineer', 'role']


@admin.register(SiteHoliday)
class SiteHolidayAdmin(CustomModelAdmin):
    list_filter = base_model_list_filter_base + (
        ('site', RelatedOnlyFieldListFilter),
        'date',
    )
    search_fields = ['name', 'summary', 'date']


@admin.register(Leave)
class LeaveAdmin(CustomModelAdmin):
    list_filter = base_model_list_filter_base + (
        'start_date',
        'end_date',
        'status',
        ('engineer', RelatedOnlyFieldListFilter),
    )
    search_fields = ['name', 'engineer', 'summary', 'start_date', 'end_date', ]
