# Staged frontend readiness

The production release for merge commit `c771eaf` stopped before promotion:
the newly created Vercel staging address returned HTTP 404 on its first root
request. All 12 quality jobs had passed and the backend deployment completed.
The same staging address subsequently loaded the actual Clinic login page.
The failure was retained in the release evidence; it was not treated as a pass.

The smoke checker now waits up to 120 seconds for the frontend root address
when it receives 404, 502, 503 or 504. It retries only read requests to that
same address. A persistent unavailable response still blocks promotion.
Authentication failures and redirects fail immediately; deployment protection
and redirect restrictions remain enabled. TLS and other transport errors are
not hidden by this readiness loop.

After readiness, the existing checks still require Clinic HTML, healthy API,
database-backed closed Owner registration, uncached API responses, OpenAPI,
Swagger, and 401 on an anonymous Dashboard request. Promotion still verifies
the exact staged deployment and production target.

Validation: `python -m unittest discover -s scripts/tests -v` covers transient
and persistent readiness errors, immediate authentication/redirect failure,
transport failure, and rejection of successful responses containing another
website. A successful production workflow remains the final hosted proof.
