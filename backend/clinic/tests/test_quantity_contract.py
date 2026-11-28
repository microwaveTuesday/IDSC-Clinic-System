from django.test import TestCase

from clinic.serializers import MedicineDispensationSerializer


class QuantityContractTests(TestCase):
    def test_serializer_uses_the_portable_positive_integer_range(self):
        serializer = MedicineDispensationSerializer()
        self.assertEqual(serializer.fields["quantity"].min_value, 1)
        self.assertEqual(serializer.fields["quantity"].max_value, 2_147_483_647)
        for quantity, valid in [(1, True), (2_147_483_647, True), (2_147_483_648, False)]:
            with self.subTest(quantity=quantity):
                candidate = MedicineDispensationSerializer(data={
                    "student_id": "SHOWCASE-001",
                    "medicine_id": "SHOWCASE-MED-001",
                    "quantity": quantity,
                })
                self.assertEqual(candidate.is_valid(), valid)
                if not valid:
                    self.assertIn("quantity", candidate.errors)

    def test_request_and_response_schema_match_the_deployed_integer_range(self):
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        schemas = response.json()["components"]["schemas"]
        for name in ["MedicineDispensation", "MedicineDispensationRequest"]:
            with self.subTest(schema=name):
                quantity = schemas[name]["properties"]["quantity"]
                self.assertEqual(quantity["minimum"], 1)
                self.assertEqual(quantity["maximum"], 2_147_483_647)
                self.assertNotEqual(quantity.get("format"), "int64")
