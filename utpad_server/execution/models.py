from django.db import models

from core.models import OrgModel, OrgGroup
from core.storage import CustomFileSystemStorage
from utpad_server import settings


class Attachment(OrgModel):
    name = models.CharField(max_length=256)
    file = models.FileField(storage=CustomFileSystemStorage, upload_to=settings.MEDIA_BASE_NAME, blank=False,
                            null=False)


class Tag(OrgModel):
    name = models.CharField(max_length=256, )
    summary = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class ProgramIncrement(OrgModel):
    name = models.CharField(max_length=256)
    summary = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class Epic(OrgModel):
    pi = models.ForeignKey(ProgramIncrement, null=True, on_delete=models.SET_NULL, related_name='epics')
    name = models.CharField(max_length=256)
    summary = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='epic_attachments', blank=True)


class Feature(OrgModel):
    epic = models.ForeignKey(Epic, null=True, on_delete=models.SET_NULL, related_name='features')
    name = models.CharField(max_length=256)
    summary = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='feature_attachments', blank=True)


class Sprint(OrgModel):
    pi = models.ForeignKey(ProgramIncrement, null=True, blank=True, on_delete=models.SET_NULL,
                           related_name='sprints')
    name = models.CharField(max_length=256)
    start_date = models.DateField(verbose_name='start date')
    end_date = models.DateField(verbose_name='end date')

    def __str__(self):
        return "Sprint-" + str(self.name) + " for release " + str(self.pi.name if self.pi else "<unset>")


class Story(OrgModel):
    class Meta:
        verbose_name_plural = "stories"

    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True)
    feature = models.ForeignKey(Feature, null=True, on_delete=models.SET_NULL, related_name='stories')
    name = models.CharField(max_length=256, )
    summary = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='story_attachments', blank=True)
    rank = models.IntegerField()


class Feedback(OrgModel):
    name = models.CharField(max_length=256, )
    summary = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    pi = models.ForeignKey(ProgramIncrement, null=True, on_delete=models.SET_NULL, related_name='feedbacks')


model_name_map = {
    'Attachment': Attachment,
    'Tag': Tag,
    'ProgramIncrement': ProgramIncrement,
    'Epic': Epic,
    'Feature': Feature,
    'Sprint': Sprint,
    'Story': Story,
    'Feedback': Feedback,
}
