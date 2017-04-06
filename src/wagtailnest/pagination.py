"""
Pagination models for DRF
"""
from rest_framework.pagination import LimitOffsetPagination


class ThousandMaxLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 1000
    max_limit = 1000
