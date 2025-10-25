from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationExtn(PageNumberPagination):
    max_page_size = 1000
    page_size = 100
    page_query_param = "page"
    page_size_query_param = "page_size"

    # def get_paginated_response(self, data):
    #     return Response({
    #         'content': data,
    #         'links': {
    #             'next': self.get_next_link(),
    #             'prev': self.get_previous_link(),
    #         }
    #     })
