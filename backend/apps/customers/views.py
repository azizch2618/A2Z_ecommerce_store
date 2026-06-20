"""Customer API views."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.customers.models import Address
from apps.customers.permissions import IsCustomerOwner
from apps.customers.serializers import AddressSerializer
from apps.customers.services import CustomerService


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = CustomerService.get_for_user(self.request.user)
        if not customer:
            return Address.objects.none()
        return customer.addresses.all()

    def perform_create(self, serializer):
        customer = CustomerService.get_for_user(self.request.user)
        serializer.save(customer=customer)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsCustomerOwner]
    lookup_field = "public_id"

    def get_queryset(self):
        customer = CustomerService.get_for_user(self.request.user)
        if not customer:
            return Address.objects.none()
        return customer.addresses.all()
