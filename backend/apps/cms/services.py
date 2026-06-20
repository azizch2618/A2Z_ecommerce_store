from apps.cms.models import BlogPost, Page


class CMSService:
    @staticmethod
    def get_published_page(slug: str) -> Page:
        return Page.objects.prefetch_related("blocks").get(slug=slug, status=Page.Status.PUBLISHED)

    @staticmethod
    def list_published_posts():
        return BlogPost.objects.filter(status="published").order_by("-published_at")
