from django.urls import include, path
from rest_framework import routers

from .views import ExecutionAttachmentViewSet, ExecutionTagViewSet, ProgramIncrementViewSet, EpicViewSet, ExecutionFeatureViewSet, SprintViewSet, \
    StoryViewSet, FeedbackViewSet

router = routers.DefaultRouter()

router.register(r'attachments', ExecutionAttachmentViewSet)
router.register(r'tags', ExecutionTagViewSet)
router.register(r'program_increments', ProgramIncrementViewSet)
router.register(r'epics', EpicViewSet)
router.register(r'features', ExecutionFeatureViewSet)
router.register(r'sprints', SprintViewSet)
router.register(r'stories', StoryViewSet)
router.register(r'feedbacks', FeedbackViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
]
