"""Customers URL routing."""
from django.urls import path

from apps.customers.views import AddressDetailView, AddressListCreateView

app_name = "customers"

urlpatterns = [
    path("addresses/", AddressListCreateView.as_view(), name="address-list"),
    path("addresses/<uuid:public_id>/", AddressDetailView.as_view(), name="address-detail"),
]
