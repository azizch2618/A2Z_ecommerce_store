from django.urls import path

from apps.payroll import views

urlpatterns = [
    path("admin/dashboard/", views.PayrollDashboardView.as_view(), name="payroll-dashboard"),
    path("admin/periods/", views.PayrollPeriodListCreateView.as_view(), name="payroll-periods"),
    path("admin/periods/<uuid:period_id>/", views.PayrollPeriodDetailView.as_view(), name="payroll-period-detail"),
    path(
        "admin/periods/<uuid:period_id>/calculate/",
        views.PayrollPeriodCalculateView.as_view(),
        name="payroll-period-calculate",
    ),
    path(
        "admin/periods/<uuid:period_id>/approve/",
        views.PayrollPeriodApproveView.as_view(),
        name="payroll-period-approve",
    ),
    path(
        "admin/periods/<uuid:period_id>/post/",
        views.PayrollPeriodPostView.as_view(),
        name="payroll-period-post",
    ),
    path(
        "admin/periods/<uuid:period_id>/adjustments/",
        views.PayrollPeriodAdjustmentView.as_view(),
        name="payroll-period-adjustment",
    ),
    path(
        "admin/salary-structures/",
        views.SalaryStructureListCreateView.as_view(),
        name="payroll-salary-structures",
    ),
    path("admin/payslips/", views.PayslipListView.as_view(), name="payroll-payslips"),
    path("admin/payslips/<uuid:payslip_id>/", views.PayslipDetailView.as_view(), name="payroll-payslip-detail"),
    path("admin/payslips/<uuid:payslip_id>/pdf/", views.PayslipPdfView.as_view(), name="payroll-payslip-pdf"),
    path(
        "admin/employees/<uuid:employee_id>/payroll-history/",
        views.EmployeePayrollHistoryView.as_view(),
        name="payroll-employee-history",
    ),
]
