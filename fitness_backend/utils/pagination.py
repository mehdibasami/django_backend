from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class that extends DRF's PageNumberPagination.
    """
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to override
    max_page_size = 100  # Maximum items per page

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,  # Add this line
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
