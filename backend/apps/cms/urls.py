from django.urls import path

from apps.cms.views import BlogPostListView, PageDetailView

app_name = "cms"

urlpatterns = [
    path("pages/<slug:slug>/", PageDetailView.as_view(), name="page-detail"),
    path("blog/", BlogPostListView.as_view(), name="blog-list"),
]
