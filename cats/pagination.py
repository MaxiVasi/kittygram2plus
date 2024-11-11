from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CatsPagination(PageNumberPagination):
    page_size = 2


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'response': data
        })
