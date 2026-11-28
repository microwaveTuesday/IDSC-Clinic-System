"""Read-only smoke checks for an HTTPS release; never creates users or clinic data."""

import json
import os
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

try:
    from .prepare_cloud_frontend import https_origin
except ImportError:  # Direct invocation by the release workflow.
    from prepare_cloud_frontend import https_origin


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def frontend_ready(origin, headers, *, opener=None, sleep=time.sleep,
                   now=time.monotonic, timeout=120):
    """Wait for the new address, without weakening any content/auth checks."""
    opener = opener or build_opener(NoRedirect)
    deadline = now() + timeout
    while True:
        remaining = deadline - now()
        if remaining <= 0:
            raise RuntimeError("Frontend readiness timed out; promotion is blocked.")
        try:
            with opener.open(Request(origin + "/", headers=headers),
                             timeout=min(30, remaining)) as response:
                return response.headers, response.read(2_000_000)
        except HTTPError as exc:
            # A just-created Vercel address can briefly return 404 before its
            # routes propagate. Auth failures and redirects must fail at once.
            if exc.code not in {404, 502, 503, 504}:
                raise
            exc.close()
            remaining = deadline - now()
            if remaining <= 0:
                raise RuntimeError("Frontend readiness timed out; promotion is blocked.") from None
            print("Frontend address not ready; retrying within the readiness deadline.")
            sleep(min(10, remaining))


def check(origin):
    origin = https_origin(origin)
    headers = {"Accept": "*/*"}
    bypass = os.environ.get("VERCEL_AUTOMATION_BYPASS_SECRET")
    if bypass:
        headers["x-vercel-protection-bypass"] = bypass

    def get(path):
        # Do not send a deployment-protection bypass header through redirects.
        with build_opener(NoRedirect).open(Request(origin + path, headers=headers), timeout=30) as response:
            return response.headers, response.read(2_000_000)

    _, page = frontend_ready(origin, headers)
    if b'<html' not in page.lower() or b'IDSC' not in page:
        raise ValueError("The deployed frontend is not the Clinic website.")
    _, body = get("/health")
    if json.loads(body).get("status") != "ok":
        raise ValueError("The public health route did not return the Clinic API response.")
    headers_out, body = get("/api/auth/setup/")
    owner_setup = json.loads(body).get("owner_registration_available")
    if not isinstance(owner_setup, bool):
        raise ValueError("The same-origin API/DB setup check failed.")
    if owner_setup:
        raise ValueError("Provision the hosted Owner privately before publishing the frontend.")
    if "no-store" not in headers_out.get("Cache-Control", ""):
        raise ValueError("The public API response must not be cached.")
    _, body = get("/api/schema/")
    if b'openapi' not in body:
        raise ValueError("The deployed contract is unavailable.")
    _, body = get("/docs")
    if b'swagger' not in body.lower():
        raise ValueError("The public Swagger page is unavailable.")
    try:
        get("/api/v1/dashboard/")
    except HTTPError as exc:
        if exc.code != 401:
            raise ValueError("The dashboard did not enforce authentication.") from None
    else:
        raise ValueError("The dashboard unexpectedly allowed anonymous access.")
    print("PASS: public frontend, health, database-backed setup, no-store API, contract, Swagger and protected dashboard.")


if __name__ == "__main__":
    check(os.environ["CLINIC_PUBLIC_ORIGIN"])
