from django.db import models
from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models import Q, TextField

from utpad_server import settings
from .storage import CustomFileSystemStorage

# Create your models here.


User.add_to_class('to_relation_representation', lambda self: {'id': self.id, 'name': self.username})
Group.add_to_class('to_relation_representation', lambda self: {'id': self.id, 'name': self.name})


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False, verbose_name='is published content')
    is_public = models.BooleanField(default=False, verbose_name='is public content')

    def __str__(self):
        if hasattr(self, 'name'):
            string_value = str(self.name)
            if hasattr(self, 'summary'):
                if self.summary is not None:
                    string_value = string_value + ":" + str(self.summary)
        else:
            string_value = str(self.id)
        return string_value

    def to_relation_representation(self):
        representation = {'id': self.id}
        if hasattr(self, 'name'):
            representation['name'] = self.name
        if hasattr(self, 'summary') and self.summary:
            representation['summary'] = self.summary
        return representation

    def is_consumer(self, user):
        return user is not None

    def is_guest(self, user):
        return user is not None

    def is_member(self, user):
        return user is not None

    def is_owner(self, user):
        return user is not None

    def can_read(self, user):
        return (self.published and self.is_public) or self.is_owner(user) or self.is_member(user) or self.is_guest(
            user) or (self.published and self.is_consumer(user))

    def can_modify(self, user):
        return self.is_owner(user) or self.is_member(user)

    def can_delete(self, user):
        return self.is_owner(user)

    def get_list_query_set(self, user):
        return self.objects.all()


base_model_base_fields = [
    'id',
    'created_at',
    'updated_at',
    'published',
    'is_public',
]


class UserMode(BaseModel):
    class Meta:
        abstract = True

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="%(class)ss")

    def is_owner(self, user):
        return (self.user is None) or (self.user == user)

    def is_member(self, user):
        return (self.user is None) or (self.user == user)

    def is_guest(self, user):
        return (self.user is None) or (self.user == user)

    def is_consumer(self, user):
        return (self.user is None) or (self.user == user)

    def can_read(self, user):
        return (self.user is None) or (self.user == user) or (self.published and self.is_public)

    def can_modify(self, user):
        return (self.user is None) or (self.user == user)

    def can_delete(self, user):
        return (self.user is None) or (self.user == user)

    def get_list_query_set(self, user):
        if user is not None:
            if user.is_superuser:
                return self.objects.all()
            else:
                return self.objects.filter(Q(user=user) | Q(user_isnull=True)).distinct()
        else:
            return self.objects.none()


class Configuration(BaseModel):
    class Meta:
        permissions = (
            ("tool_integration_read",
             "Integration Read permission to integrate CI/CT tool typically used with an Auth Token."),
            ("tool_integration_write",
             "Integration Write permission to integrate CI/CT tool typically used with an Auth Token."),
            ("tool_integration_delete",
             "Integration Delete permission to integrate CI/CT tool typically used with an Auth Token."),
        )

    name = models.CharField(max_length=256, unique=True)
    value = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name) + ": " + str(self.value)


def get_database_name():
    database_name_config = Configuration.objects.filter(name="site_name")
    if database_name_config.count() > 0:
        return database_name_config[0].value
    return "Utpad Team Management"


# noinspection PyUnresolvedReferences
class OrgGroup(BaseModel):
    name = models.CharField(max_length=256, unique=True)
    auth_group = models.OneToOneField(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name="org_group",
                                      verbose_name='authorization group')
    summary = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    org_group = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="sub_org_groups", verbose_name='parent organization group')
    leaders = models.ManyToManyField(User, blank=True, related_name="org_groups_where_leader")
    members = models.ManyToManyField(User, blank=True, related_name="org_groups_where_member")
    guests = models.ManyToManyField(User, blank=True, related_name="org_groups_where_guest")
    consumers = models.ManyToManyField(User, blank=True, related_name="org_groups_where_consumer")

    def is_owner(self, user):
        return ((self.leaders is not None) and (user in self.leaders.all())) or (
                (self.org_group is not None) and self.org_group.is_owner(user))

    def is_member(self, user):
        return ((self.members is not None) and (user in self.members.all())) or (
                (self.org_group is not None) and self.org_group.is_member(user))

    def is_guest(self, user):
        return ((self.guests is not None) and (user in self.guests.all())) or (
                (self.org_group is not None) and self.org_group.is_guest(user))

    def is_consumer(self, user):
        return ((self.consumers is not None) and (user in self.consumers.all())) or (
                (self.org_group is not None) and self.org_group.is_consumer(user))

    def can_read(self, user):
        return (self.published and self.is_public) or self.is_consumer(user) or self.is_guest(user) or self.is_member(
            user) or self.is_owner(user)

    def can_modify(self, user):
        return self.is_owner(user) or self.is_member(user)

    def can_delete(self, user):
        return self.is_owner(user)

    def get_transitive_sub_groups(self):
        transitive_sub_orgs = [self.id]
        direct_sub_orgs = OrgGroup.objects.filter(Q(org_group__pk=self.id))
        for direct_sub_org in direct_sub_orgs:
            transitive_sub_orgs.extend(direct_sub_org.get_transitive_sub_groups())
        return transitive_sub_orgs

    def get_list_query_set(self, user):
        user_id = user.id if user else None

        if user is not None:
            if user.is_superuser:
                return self.objects.all()
            elif user.is_anonymous:
                return self.objects.filter(Q(published='True') & Q(is_public='True')).distinct()
            else:
                org_groups_where_read_privilege = user.get_orgs_with_view_privileges()
                org_groups_where_consumer_privilege = user.get_orgs_with_consumer_privileges()

                # Q(org_group__isnull=True)|
                return self.objects.filter((
                                                   Q(published='True') &
                                                   Q(is_public='True')
                                           )
                                           | (
                                                   Q(published='True') &
                                                   Q(pk__in=org_groups_where_consumer_privilege)
                                           )
                                           | Q(pk__in=org_groups_where_read_privilege)
                                           ).distinct()

                # return self.objects.filter(Q(org_group__isnull=True)
                #                            | (Q(published='True') & Q(is_public='True'))
                #                            | Q(consumers__pk=user_id)  # No need published check for ORG_GROUP Model
                #                            | Q(guests__pk=user_id)
                #                            | Q(members__pk=user_id)
                #                            | Q(leaders__pk=user_id)
                #                            ).distinct()
        else:
            return self.objects.none()


# Extend User model for org group based object permissions helper functions

def get_orgs_with_delete_privileges(user):
    org_id_where_owner = []
    orgs_with_direct_owner_privileges = OrgGroup.objects.filter(Q(leaders__pk=user.id))

    for org_with_direct_owner_privileges in orgs_with_direct_owner_privileges:
        transitive_sub_groups = org_with_direct_owner_privileges.get_transitive_sub_groups()
        org_id_where_owner.extend(transitive_sub_groups)

    return list(set(org_id_where_owner))


User.add_to_class('get_orgs_with_delete_privileges', get_orgs_with_delete_privileges)


def get_orgs_with_change_privileges(user):
    org_id_where_member = user.get_orgs_with_delete_privileges()
    orgs_with_direct_member_privileges = OrgGroup.objects.filter(Q(members__pk=user.id))

    for org_with_direct_owner_privileges in orgs_with_direct_member_privileges:
        transitive_sub_groups = org_with_direct_owner_privileges.get_transitive_sub_groups()
        org_id_where_member.extend(transitive_sub_groups)

    return list(set(org_id_where_member))


User.add_to_class('get_orgs_with_change_privileges', get_orgs_with_change_privileges)


def get_orgs_with_view_privileges(user):
    org_id_where_guest = user.get_orgs_with_change_privileges()
    orgs_with_direct_guest_privileges = OrgGroup.objects.filter(Q(guests__pk=user.id))

    for org_with_direct_owner_privileges in orgs_with_direct_guest_privileges:
        transitive_sub_groups = org_with_direct_owner_privileges.get_transitive_sub_groups()
        org_id_where_guest.extend(transitive_sub_groups)

    return list(set(org_id_where_guest))


User.add_to_class('get_orgs_with_view_privileges', get_orgs_with_view_privileges)


def get_orgs_with_consumer_privileges(user):
    org_id_where_consumer = []
    orgs_with_direct_consumer_privileges = OrgGroup.objects.filter(Q(consumers__pk=user.id))

    for org_with_direct_owner_privileges in orgs_with_direct_consumer_privileges:
        transitive_sub_groups = org_with_direct_owner_privileges.get_transitive_sub_groups()
        org_id_where_consumer.extend(transitive_sub_groups)

    return list(set(org_id_where_consumer))


User.add_to_class('get_orgs_with_consumer_privileges', get_orgs_with_consumer_privileges)


# noinspection PyUnresolvedReferences
class OrgModel(BaseModel):
    class Meta:
        abstract = True

    org_group = models.ForeignKey(OrgGroup, on_delete=models.SET_NULL, blank=True, null=True,
                                  verbose_name='organization group', related_name='%(app_label)s_%(class)s')

    def is_owner(self, user):
        return (
                (self.org_group is None) or
                self.org_group.is_owner(user)
        )

    def is_member(self, user):
        return (
                (self.org_group is None) or
                self.org_group.is_member(user)
        )

    def is_guest(self, user):
        return (
                (self.org_group is None) or
                self.org_group.is_guest(user)
        )

    def is_consumer(self, user):
        return (
                (self.org_group is None) or
                self.org_group.is_consumer(user)
        )

    def can_read(self, user):
        return (
                (self.org_group is None) or
                self.is_owner(user) or
                self.is_member(user) or
                self.is_guest(user) or
                (self.published and self.is_consumer(user)) or
                (self.published and self.is_public)
        )

    def can_modify(self, user):
        return (
                (self.org_group is None)
                or self.is_owner(user)
                or self.is_member(user)
        )

    def can_delete(self, user):
        return (
                (self.org_group is None) or
                self.is_owner(user)
        )

    def get_list_query_set(self, user):
        if user is not None:
            if user.is_superuser:
                return self.objects.all()
            elif user.is_anonymous:
                return self.objects.filter(
                    Q(published='True') & (Q(is_public='True') | Q(org_group__isnull=True))).distinct()
            else:
                org_groups_where_read_privilege = user.get_orgs_with_view_privileges()
                org_groups_where_consumer_privilege = user.get_orgs_with_consumer_privileges()

                return self.objects.filter(Q(org_group__isnull=True)
                                           | (
                                                   Q(published='True') &
                                                   Q(is_public='True')
                                           )
                                           | (
                                                   Q(published='True') &
                                                   Q(org_group__pk__in=org_groups_where_consumer_privilege)
                                           )
                                           | Q(org_group__pk__in=org_groups_where_read_privilege)
                                           ).distinct()
                # user_id = user.id if user else None
                # return self.objects.filter(Q(org_group__isnull=True)
                #                            | (Q(published='True') & (Q(is_public='True')))
                #                            | (Q(published='True') & Q(org_group__consumers__pk=user_id))
                #                            | Q(org_group__guests__pk=user_id)
                #                            | Q(org_group__members__pk=user_id)
                #                            | Q(org_group__leaders__pk=user_id)
                #                            ).distinct()
        else:
            return self.objects.none()


org_model_base_fields = base_model_base_fields + ['org_group', ]


class NotMutablePublishOrgModel(OrgModel):
    class Meta:
        abstract = True

    def can_modify(self, user):
        return (self.org_group is None) or (not self.published and (self.is_owner(user) or self.is_member(user)))

    def can_delete(self, user):
        return (self.org_group is None) or (not self.published and self.is_owner(user))


class Attachment(OrgModel):
    name = models.CharField(max_length=256)
    file = models.FileField(storage=CustomFileSystemStorage, upload_to=settings.MEDIA_BASE_NAME, blank=False,
                            null=False)


class Site(OrgModel):
    name = models.CharField(max_length=256)
    summary = models.CharField(max_length=256, null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='site_attachments', blank=True)


class PythonCodeField(TextField):
    pass


class XMLField(TextField):
    pass


class GherkinField(TextField):
    pass


class HTMLField(TextField):
    pass


class LuaField(TextField):
    pass


model_name_map = {
    # User and Group modeles are directly mapped in the data_loader
    'Configuration': Configuration,
    'OrgGroup': OrgGroup,
    'Attachment': Attachment,
    'Site': Site,
}
