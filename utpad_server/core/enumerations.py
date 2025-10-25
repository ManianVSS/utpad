from django.db import models
from django.utils.translation import gettext_lazy as _


class ReviewStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft'),
    IN_PROGRESS = 'IN_PROGRESS', _('In progress'),
    IN_REVIEW = 'IN_REVIEW', _('In Review'),
    APPROVED = 'APPROVED', _('Approved'),
