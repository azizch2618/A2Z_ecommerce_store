"""Health endpoint tests."""
from django.test import TestCase


class HealthEndpointTests(TestCase):
    def test_liveness(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_readiness(self):
        response = self.client.get("/api/v1/ready/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["checks"]["database"], "ok")
