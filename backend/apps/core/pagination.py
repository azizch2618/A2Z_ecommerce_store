"""Cursor pagination aligned with API specification."""
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class A2ZCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100
    ordering = "-created_at"

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "data": schema,
                "pagination": {
                    "type": "object",
                    "properties": {
                        "next_cursor": {"type": "string", "nullable": True},
                        "has_more": {"type": "boolean"},
                        "limit": {"type": "integer"},
                    },
                },
            },
        }

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "pagination": {
                    "next_cursor": self.get_next_link(),
                    "has_more": self.get_next_link() is not None,
                    "limit": self.get_page_size(self.request),
                },
            }
        )