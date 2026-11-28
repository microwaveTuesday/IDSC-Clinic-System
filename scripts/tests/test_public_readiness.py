import io
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from scripts.check_public_deployment import check, frontend_ready


class Response(io.BytesIO):
    headers = {"Content-Type": "text/html"}


class FrontendReadinessTests(unittest.TestCase):
    def provider(self, outcomes):
        calls = []
        outcomes = iter(outcomes)

        class Opener:
            def open(self, request, timeout):
                calls.append((request, timeout))
                outcome = next(outcomes)
                if isinstance(outcome, Exception):
                    raise outcome
                if isinstance(outcome, int):
                    raise HTTPError(request.full_url, outcome, "Synthetic response", {}, io.BytesIO())
                return Response(outcome)

        return Opener(), calls

    def clock(self):
        elapsed = [0]
        return lambda: elapsed[0], lambda seconds: elapsed.__setitem__(0, elapsed[0] + seconds)

    def test_new_address_404_then_503_then_real_content(self):
        opener, calls = self.provider([404, 503, b"<html>IDSC Clinic</html>"])
        now, sleep = self.clock()
        _, body = frontend_ready("https://clinic.example.test", {}, opener=opener, now=now, sleep=sleep)
        self.assertIn(b"IDSC Clinic", body)
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(call[0].full_url == "https://clinic.example.test/" for call in calls))

    def test_persistent_404_stops_at_deadline(self):
        opener, calls = self.provider([404] * 10)
        now, sleep = self.clock()
        with self.assertRaisesRegex(RuntimeError, "promotion is blocked"):
            frontend_ready("https://clinic.example.test", {}, opener=opener, now=now, sleep=sleep, timeout=20)
        self.assertEqual(len(calls), 2)
        self.assertEqual(now(), 20)

    def test_auth_and_redirect_errors_are_not_retried(self):
        for status in [301, 302, 307, 308, 400, 401, 403]:
            with self.subTest(status=status):
                opener, calls = self.provider([status])
                with self.assertRaises(HTTPError) as error:
                    frontend_ready("https://clinic.example.test", {}, opener=opener)
                self.assertEqual(error.exception.code, status)
                self.assertEqual(len(calls), 1)

    def test_connection_or_certificate_failure_is_not_hidden(self):
        opener, calls = self.provider([URLError("Synthetic TLS or transport failure")])
        with self.assertRaises(URLError):
            frontend_ready("https://clinic.example.test", {}, opener=opener)
        self.assertEqual(len(calls), 1)

    def test_wrong_success_content_is_returned_for_existing_strict_checks(self):
        opener, calls = self.provider([b"<html>Wrong app</html>"])
        _, body = frontend_ready("https://clinic.example.test", {}, opener=opener)
        self.assertEqual(body, b"<html>Wrong app</html>")
        self.assertEqual(len(calls), 1)
        with patch("scripts.check_public_deployment.frontend_ready", return_value=({}, body)):
            with self.assertRaisesRegex(ValueError, "not the Clinic website"):
                check("https://clinic.example.test")


if __name__ == "__main__":
    unittest.main()
