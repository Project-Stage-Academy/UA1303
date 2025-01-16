from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from projects.models import Project
from profiles.models import StartupProfile

User = get_user_model()
@registry.register_document
class StartupDocument(Document):
    user = fields.ObjectField(properties={
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
        'email': fields.TextField(),
    })

    class Index:
        name = 'startups'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = StartupProfile
        fields = [
            'company_name',
            'industry',
            'country',
            'city',
            'description',
        ]
        related_models = [User]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.startup_profile


@registry.register_document
class ProjectDocument(Document):
    startup = fields.ObjectField(properties={
        'company_name': fields.TextField(),
        'industry': fields.TextField(),
    })

    description = fields.ObjectField(properties={
        'description': fields.TextField(),
    })

    class Index:
        name = 'projects'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Project
        fields = [
            'title',
            'funding_goal',
            'is_published',
            'is_completed',
            'created_at',
            'updated_at',
        ]
        related_models = [StartupProfile, Description]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, StartupProfile):
            return related_instance.projects.all()
        elif isinstance(related_instance, Description):
            return related_instance.project
