import unittest
from alder_sav.utils.api import (
    call_api_endpoint,
    validate_api_response,
    get_api_schema,
    list_api_endpoints,
    paginate_api_results
)

class TestAPIManager(unittest.TestCase):
    """Tests unitaires pour la gestion des API."""

    def test_call_api_endpoint(self):
        response = call_api_endpoint("/clients", method="GET")
        self.assertTrue("status" in response)
        self.assertIn(response["status"], [200, 201, 204])

    def test_validate_api_response(self):
        response = {"status": 200, "data": [{"id": "CLT-001"}]}
        self.assertTrue(validate_api_response(response))
        self.assertFalse(validate_api_response({"status": 500}))

    def test_get_api_schema(self):
        schema = get_api_schema("/clients")
        self.assertIn("fields", schema)
        self.assertIn("methods", schema)

    def test_list_api_endpoints(self):
        endpoints = list_api_endpoints()
        self.assertTrue(isinstance(endpoints, list))
        self.assertTrue(any("/clients" in e["path"] for e in endpoints))

    def test_paginate_api_results(self):
        results = [{"id": f"CLT-{i:03d}"} for i in range(50)]
        page = paginate_api_results(results, page=2, page_size=10)
        self.assertEqual(len(page), 10)
        self.assertEqual(page[0]["id"], "CLT-010")

if __name__ == '__main__':
    unittest.main() 