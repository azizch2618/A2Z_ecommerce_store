from rest_framework import serializers

from apps.cms.models import BlogPost, Page, PageBlock


class PageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBlock
        fields = ("block_type", "content", "sort_order")


class PageSerializer(serializers.ModelSerializer):
    blocks = PageBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ("slug", "title", "meta_title", "meta_description", "blocks")
        read_only_fields = fields


class BlogPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ("slug", "title", "excerpt", "published_at")
        read_only_fields = fields
