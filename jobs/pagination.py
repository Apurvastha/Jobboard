from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class JobListingPagination(PageNumberPagination):

    # default page size 
    page_size = 20
    
    # client can override page size with ?page_size = 50
    page_size_query_param = 'page_size'

    # maximum page size - prevent abuse
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_page': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
    
    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'current_page': {'type': 'integer'},
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'results': schema,
            }
        }