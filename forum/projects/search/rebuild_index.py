from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.registries import registry


class Command(BaseCommand):
    help = "Rebuild ElasticSearch indexes"

    def handle(self, *args, **kwargs):
        for index in registry.get_indices():
            index.delete(ignore=404)
            index.create()

        for doc in registry.get_documents():
            qs = doc().get_queryset()
            doc().update(qs)

        self.stdout.write(self.style.SUCCESS('Successfully rebuilt index'))
