from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from projects.models import Project
from profiles.models import StartupProfile

startup_index = Index('startups')
project_index = Index('projects')

User = get_user_model()


@startup_index.doc_type
class StartupDocument(Document):
    class Django:
        model = StartupProfile
        fields = [
            'company_name',
            'size',
            'country',
            'city',
            'created_at',
        ]


@registry.register_document
class ProjectDocument(Document):
    startup = fields.ObjectField(properties={
        'name': fields.TextField(),
        'description': fields.TextField(),
    })

    class Index:
        name = 'projects'

    class Django:
        model = Project
        fields = [
            'title',
            'is_completed',
            'created_at',
            'funding_goal',
        ]
