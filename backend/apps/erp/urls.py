"""ERP platform URL routing."""
from django.urls import path

from apps.erp import views

app_name = "erp"

urlpatterns = [
    path("company/", views.CompanyDetailView.as_view(), name="company"),
    path("settings/", views.PlatformSettingListView.as_view(), name="settings"),
    path("audit/", views.AuditEventListView.as_view(), name="audit"),
    path("sequences/", views.DocumentSequenceListView.as_view(), name="sequences"),
    path("parties/", views.PartyListView.as_view(), name="party-list"),
    path("parties/sync/", views.PartySyncView.as_view(), name="party-sync"),
    path(
        "parties/<uuid:party_id>/contacts/",
        views.PartyContactListCreateView.as_view(),
        name="party-contacts",
    ),
    path(
        "parties/<uuid:party_id>/addresses/",
        views.PartyAddressListCreateView.as_view(),
        name="party-addresses",
    ),
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/<uuid:notification_id>/read/",
        views.NotificationMarkReadView.as_view(),
        name="notification-read",
    ),
    path("workflows/definitions/", views.WorkflowDefinitionListView.as_view(), name="workflow-defs"),
    path(
        "workflows/instances/<uuid:instance_id>/",
        views.WorkflowInstanceDetailView.as_view(),
        name="workflow-instance",
    ),
    path(
        "workflows/instances/<uuid:instance_id>/transition/",
        views.WorkflowTransitionView.as_view(),
        name="workflow-transition",
    ),
    path("events/", views.DomainEventListView.as_view(), name="events"),
]
