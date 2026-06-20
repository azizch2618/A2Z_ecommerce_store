from rest_framework import generics

from apps.cms.permissions import IsCMSReadOnly
from apps.cms.serializers import BlogPostListSerializer, PageSerializer
from apps.cms.services import CMSService


class PageDetailView(generics.RetrieveAPIView):
    serializer_class = PageSerializer
    permission_classes = [IsCMSReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        from apps.cms.models import Page

        return Page.objects.filter(status=Page.Status.PUBLISHED).prefetch_related("blocks")


class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer
    permission_classes = [IsCMSReadOnly]

    def get_queryset(self):
        return CMSService.list_published_posts()
