"""CRM URL routing."""
from django.urls import path

from apps.crm import views

urlpatterns = [
    path("admin/dashboard/", views.CrmDashboardView.as_view(), name="crm-admin-dashboard"),
    path("admin/meta/", views.CrmMetaView.as_view(), name="crm-admin-meta"),
    path("admin/leads/", views.CrmLeadListCreateView.as_view(), name="crm-admin-leads"),
    path("admin/leads/<uuid:lead_id>/", views.CrmLeadDetailView.as_view(), name="crm-admin-lead-detail"),
    path(
        "admin/leads/<uuid:lead_id>/convert/",
        views.CrmLeadConvertView.as_view(),
        name="crm-admin-lead-convert",
    ),
    path(
        "admin/opportunities/",
        views.CrmOpportunityListCreateView.as_view(),
        name="crm-admin-opportunities",
    ),
    path(
        "admin/opportunities/<uuid:opportunity_id>/",
        views.CrmOpportunityDetailView.as_view(),
        name="crm-admin-opportunity-detail",
    ),
    path("admin/activities/", views.CrmActivityListCreateView.as_view(), name="crm-admin-activities"),
    path("admin/notes/", views.CrmNoteListCreateView.as_view(), name="crm-admin-notes"),
    path("admin/timeline/", views.CrmTimelineView.as_view(), name="crm-admin-timeline"),
    path("admin/pipeline/", views.CrmPipelineView.as_view(), name="crm-admin-pipeline"),
]
