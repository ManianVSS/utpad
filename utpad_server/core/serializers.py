from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, ManyRelatedField

from .models import Attachment, OrgGroup, Configuration, Site, base_model_base_fields, org_model_base_fields


class ServerModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.expand_relation_as_object = kwargs.pop('expand_relation_as_object', True)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        super_representation = super().to_representation(instance)

        if self.expand_relation_as_object:
            fields = self._readable_fields

            for field in fields:
                attribute = field.get_attribute(instance)
                instance_field = getattr(instance, field.field_name)
                if instance_field:
                    if isinstance(field, PrimaryKeyRelatedField):
                        if hasattr(instance_field, 'to_relation_representation'):
                            super_representation[field.field_name] = instance_field.to_relation_representation()
                        else:
                            super_representation[field.field_name] = {'id': instance_field.id, }
                    elif isinstance(field, ManyRelatedField):
                        super_representation[field.field_name] = []
                        for related_item in instance_field.all():
                            if hasattr(related_item, 'to_relation_representation'):
                                repr_item_to_add = related_item.to_relation_representation()
                            else:
                                repr_item_to_add = {'id': related_item.id, }
                            super_representation[field.field_name].append(repr_item_to_add)

        return super_representation


class UserSerializer(ServerModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                  'password', 'last_login', 'is_superuser', 'groups', 'user_permissions', ]


class GroupSerializer(ServerModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class ConfigurationSerializer(ServerModelSerializer):
    class Meta:
        model = Configuration
        fields = base_model_base_fields + ['name', 'value', 'description', ]


class OrgGroupSerializer(ServerModelSerializer):
    class Meta:
        model = OrgGroup
        fields = base_model_base_fields + ['name', 'summary', 'auth_group', 'description', 'org_group',
                                           'leaders', 'members', 'guests', 'consumers', ]


class AttachmentSerializer(ServerModelSerializer):
    class Meta:
        model = Attachment
        fields = org_model_base_fields + ['name', 'file', ]


class SiteSerializer(ServerModelSerializer):
    class Meta:
        model = Site
        fields = org_model_base_fields + ['name', 'summary', 'attachments', ]


serializer_map = {
    User: UserSerializer,
    Group: GroupSerializer,
    Configuration: ConfigurationSerializer,
    OrgGroup: OrgGroupSerializer,
    Attachment: AttachmentSerializer,
    Site: SiteSerializer,
}
