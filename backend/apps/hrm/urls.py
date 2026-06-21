from django.urls import path

from apps.hrm import views

urlpatterns = [
    path("admin/dashboard/", views.HrmDashboardView.as_view(), name="hrm-dashboard"),
    path("admin/org-structure/", views.OrgStructureView.as_view(), name="hrm-org"),
    path("admin/employees/", views.EmployeeListCreateView.as_view(), name="hrm-employees"),
    path("admin/employees/<uuid:employee_id>/", views.EmployeeDetailView.as_view(), name="hrm-employee-detail"),
    path(
        "admin/employees/<uuid:employee_id>/documents/",
        views.EmployeeDocumentUploadView.as_view(),
        name="hrm-employee-docs",
    ),
    path(
        "admin/employees/<uuid:employee_id>/clock-in/",
        views.AttendanceClockInView.as_view(),
        name="hrm-clock-in",
    ),
    path(
        "admin/employees/<uuid:employee_id>/clock-out/",
        views.AttendanceClockOutView.as_view(),
        name="hrm-clock-out",
    ),
    path(
        "admin/employees/<uuid:employee_id>/attendance/",
        views.AttendanceListView.as_view(),
        name="hrm-attendance",
    ),
    path("admin/leave-requests/", views.LeaveRequestListCreateView.as_view(), name="hrm-leave-list"),
    path(
        "admin/leave-requests/<uuid:request_id>/submit/",
        views.LeaveRequestSubmitView.as_view(),
        name="hrm-leave-submit",
    ),
    path(
        "admin/leave-requests/<uuid:request_id>/approve/",
        views.LeaveRequestApproveView.as_view(),
        name="hrm-leave-approve",
    ),
    path(
        "admin/leave-requests/<uuid:request_id>/reject/",
        views.LeaveRequestRejectView.as_view(),
        name="hrm-leave-reject",
    ),
    path("admin/assets/", views.AssetListCreateView.as_view(), name="hrm-assets"),
    path("admin/assets/<uuid:asset_id>/assign/", views.AssetAssignView.as_view(), name="hrm-asset-assign"),
    path(
        "admin/asset-assignments/",
        views.AssetAssignmentListView.as_view(),
        name="hrm-assignments",
    ),
    path(
        "admin/asset-assignments/<uuid:assignment_id>/return/",
        views.AssetReturnView.as_view(),
        name="hrm-asset-return",
    ),
]
