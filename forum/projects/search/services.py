from elasticsearch_dsl import Q
from .documents import StartupDocument, ProjectDocument


class SearchService:
    @staticmethod
    def search_startups(query=None, filters=None, sort_by=None):
        search = StartupDocument.search()
        if query:
            search = search.query(
                Q('multi_match',
                  query=query,
                  fields=['company_name^3', 'industry^2', 'description', 'city', 'country'])
            )

        if filters:
            for key, value in filters.items():
                if value:
                    search = search.filter('term', **{key: value})

        if sort_by:
            search = search.sort(sort_by)

        return search.execute()

    @staticmethod
    def search_projects(query=None, filters=None, sort_by=None):
        search = ProjectDocument.search()
        if query:
            search = search.query(
                Q('multi_match',
                  query=query,
                  fields=['title^3', 'startup.company_name^2', 'description.description'])
            )

        if filters:
            for key, value in filters.items():
                if value:
                    search = search.filter('term', **{key: value})

        if sort_by:
            search = search.sort(sort_by)

        return search.execute()
