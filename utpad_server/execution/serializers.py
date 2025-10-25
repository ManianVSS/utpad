from core.models import org_model_base_fields
from core.serializers import ServerModelSerializer
from .models import Attachment, Tag, ProgramIncrement, Story, Sprint, Feature, Epic, Feedback


class ExecutionAttachmentSerializer(ServerModelSerializer):
    class Meta:
        model = Attachment
        fields = org_model_base_fields + ['name', 'file', ]


class ExecutionTagSerializer(ServerModelSerializer):
    class Meta:
        model = Tag
        fields = org_model_base_fields + ['name', 'summary', 'description', ]


class ProgramIncrementSerializer(ServerModelSerializer):
    class Meta:
        model = ProgramIncrement
        fields = org_model_base_fields + ['name', 'summary', 'description', ]


class EpicSerializer(ServerModelSerializer):
    class Meta:
        model = Epic
        fields = org_model_base_fields + ['name', 'summary', 'description', 'weight', 'attachments', 'pi', ]


class ExecutionFeatureSerializer(ServerModelSerializer):
    class Meta:
        model = Feature
        fields = org_model_base_fields + ['name', 'summary', 'description', 'weight', 'attachments', 'epic', ]


class SprintSerializer(ServerModelSerializer):
    class Meta:
        model = Sprint
        fields = org_model_base_fields + ['name', 'pi', 'start_date', 'end_date', ]


class StorySerializer(ServerModelSerializer):
    class Meta:
        model = Story
        fields = org_model_base_fields + ['name', 'summary', 'description', 'weight', 'attachments', 'rank', 'sprint',
                                          'feature', ]


class FeedbackSerializer(ServerModelSerializer):
    class Meta:
        model = Feedback
        fields = org_model_base_fields + ['name', 'summary', 'description', 'time', 'pi', ]


serializer_map = {
    Attachment: ExecutionAttachmentSerializer,
    Tag: ExecutionTagSerializer,
    ProgramIncrement: ProgramIncrementSerializer,
    Epic: EpicSerializer,
    Feature: ExecutionFeatureSerializer,
    Sprint: SprintSerializer,
    Story: StorySerializer,
    Feedback: FeedbackSerializer,
}
