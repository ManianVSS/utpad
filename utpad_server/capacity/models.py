from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import OrgModel, OrgGroup, BaseModel, Site
from core.storage import CustomFileSystemStorage


class Attachment(OrgModel):
    name = models.CharField(max_length=256)
    file = models.FileField(storage=CustomFileSystemStorage, upload_to='execution', blank=False, null=False)


class Engineer(OrgModel):
    employee_id = models.CharField(max_length=20, null=True, blank=True, verbose_name='employee id')
    name = models.CharField(max_length=256, default='<unnamed>')
    auth_user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="engineer",
                                     verbose_name='authorization user')
    role = models.CharField(max_length=256, null=True, blank=True, )
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="engineers")
    points = models.FloatField(default=0)
    attachments = models.ManyToManyField(Attachment, related_name='engineer_attachments', blank=True)

    def __str__(self):
        return str(self.auth_user)

    def is_guest(self, user):
        return user == self.auth_user


class EngineerOrgGroupParticipation(OrgModel):
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="org_group_participation")
    role = models.CharField(max_length=256, null=True, blank=True, )
    capacity = models.FloatField(default=1.0)

    def __str__(self):
        return str(self.engineer) + " participates in " + str(self.org_group) + " with capacity " + str(
            self.capacity)


class SiteHoliday(BaseModel):
    name = models.CharField(max_length=256)
    date = models.DateField()
    summary = models.CharField(max_length=256, null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='site_holiday_attachments', blank=True)
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="site_holidays")

    def __str__(self):
        return str(self.site) + ": " + str(self.name) + ": " + str(self.date)

    def is_owner(self, user):
        return (self.site is not None) and (hasattr(self.site, 'is_owner') and self.site.is_owner(user))

    # noinspection PyMethodMayBeStatic
    def is_member(self, user):
        return False

    def is_guest(self, user):
        return False

    def can_read(self, user):
        return self.is_owner(user)


class LeaveStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft'),
    IN_REVIEW = 'IN_REVIEW', _('In Review'),
    APPROVED = 'APPROVED', _('Approved'),
    CLOSED = 'CLOSED', _('Closed'),


class Leave(BaseModel):
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="leaves")
    start_date = models.DateField(verbose_name='start date')
    end_date = models.DateField(verbose_name='end date')
    summary = models.CharField(max_length=256, null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='leave_attachments', blank=True)
    status = models.CharField(max_length=9, choices=LeaveStatus.choices, default=LeaveStatus.DRAFT)

    def __str__(self):
        return str(self.engineer) + " from " + str(self.start_date) + " to " + str(self.end_date) + " - " + str(
            self.status)

    def is_owner(self, user):
        return (self.engineer is not None) and (hasattr(self.engineer, 'is_owner') and self.engineer.is_owner(user))

    # noinspection PyMethodMayBeStatic
    def is_member(self, user):
        return False

    def is_guest(self, user):
        return False

    # noinspection PyUnresolvedReferences
    def can_read(self, user):
        return self.is_owner(user) or (user == self.engineer.auth_user)


model_name_map = {
    'Attachment': Attachment,
    'Engineer': Engineer,
    'EngineerOrgGroupParticipation': EngineerOrgGroupParticipation,
    'SiteHoliday': SiteHoliday,
    'Leave': Leave,
}
