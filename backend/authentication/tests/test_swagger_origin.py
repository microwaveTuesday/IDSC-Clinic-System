from urllib.parse import urljoin

from django.test import TestCase


class SwaggerOriginTests(TestCase):
    def test_schema_requests_use_the_origin_serving_the_schema(self):
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        server = schema['servers'][0]['url']
        for origin in ['https://clinic.example.test', 'http://127.0.0.1:8002']:
            resolved = urljoin(origin + '/api/schema/', server)
            self.assertEqual(urljoin(resolved, 'health'), origin + '/health')
            self.assertEqual(
                urljoin(resolved, 'api/v1/dashboard/'),
                origin + '/api/v1/dashboard/',
            )

    def test_swagger_supplies_csrf_for_same_origin_non_get_requests(self):
        response = self.client.get('/docs')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'request.credentials === "same-origin"')
        self.assertIn('X-CSRFTOKEN', response.content.decode().upper())
        self.assertIn('csrftoken', response.cookies)
