"""CMS content models."""
from django.db import models

from apps.core.models import PublicIdModel


class Page(PublicIdModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    slug = models.SlugField(max_length=150, unique=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table = "cms_pages"


class PageBlock(PublicIdModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(max_length=50)
    content = models.JSONField(default=dict)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "cms_page_blocks"
        ordering = ["sort_order"]


class BlogPost(PublicIdModel):
    slug = models.SlugField(max_length=150, unique=True)
    title = models.CharField(max_length=255)
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="blog_posts")
    status = models.CharField(max_length=20, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
    seo_meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "cms_blog_posts"


class NavigationMenu(PublicIdModel):
    class Location(models.TextChoices):
        HEADER = "header", "Header"
        FOOTER = "footer", "Footer"
        MOBILE = "mobile", "Mobile"

    location = models.CharField(max_length=20, choices=Location.choices, unique=True)
    items = models.JSONField(default=list)

    class Meta:
        db_table = "cms_navigation_menus"
