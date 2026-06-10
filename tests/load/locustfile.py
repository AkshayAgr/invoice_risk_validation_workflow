import os

from locust import HttpUser, between, task


class InvoiceValidationUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def validate_invoice(self):
        headers = {}
        token = os.getenv("LOAD_TEST_BEARER_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client.post(
            "/v1/validations",
            json={"invoice_number": "INV-2026-014"},
            headers=headers,
            name="/v1/validations",
            timeout=180,
        )
