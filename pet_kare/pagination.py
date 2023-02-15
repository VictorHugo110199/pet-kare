from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 2
    page_query_param = "page"
    max_page_size = 6
    page_size_query_param = "total_resultados"