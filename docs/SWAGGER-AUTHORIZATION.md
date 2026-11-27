# Using Swagger for the Clinic showcase

Open <https://idsc-clinic-management.vercel.app/docs>. The server must resolve to
the website serving the documentation. `127.0.0.1` points to your own computer,
so it cannot be used for the hosted demonstration. The schema now declares `/`
as its server, which supports both the hosted proxy and local development.

## Obtain and authorize a JWT

1. Open Swagger using the same hostname as the Clinic website.
2. Expand `POST /api/v1/auth/login/`, choose **Try it out**, and replace the
   example body with your own username and password. Enter these privately.
3. Choose **Execute**. Expect HTTP 200 and an `access_token` in the response.
   Swagger's same-origin request interceptor supplies the page's CSRF token.
4. Copy only the value of `access_token`, without quotation marks. Do not share
   the response, token, request body, or generated cURL command in screenshots.
5. Choose the top **Authorize** button. Under **bearerAuth (http, Bearer)**,
   paste only the token. Do not type `Bearer `; Swagger adds that prefix.
6. Choose **Authorize**, then **Close**. Leave **cookieAuth** blank.
7. Expand `GET /api/v1/dashboard/`, choose **Try it out**, then **Execute**.
   Expect HTTP 200. Check that **Request URL** starts with the live HTTPS origin.
8. Collapse the login response before projecting the screen. Clear the login
   request body when finished. Close the tab after the demonstration.

If already signed in on this hostname, `POST /api/auth/token/` can issue a new
JWT from the existing session. It is a session-only operation; a bearer token
alone is not sufficient. Normal website login already obtains and sends JWTs.

## Prove authorization rather than an existing cookie session

The API supports Django sessions as well as JWTs. Clearing Swagger's bearer
authorization in a browser that still has a signed-in session may still return
200. Use a fresh private/incognito window with no Clinic cookies and no bearer
authorization to demonstrate HTTP 401. Then authenticate a synthetic Staff
account and request `GET /api/v1/users/`: expect HTTP 403. An Owner or Admin can
manage Staff; Staff cannot. Only the Owner can manage Admins.

## Troubleshooting

| Result | Meaning and action |
| --- | --- |
| Request URL contains localhost/127.0.0.1 | The old schema is still deployed. Release the same-origin server fix and reload Swagger. Re-entering a token cannot fix the destination. |
| Failed to fetch | Check Request URL and `/health`. A sleeping backend may need time to wake. Do not repeatedly submit a write. |
| 400 | Inspect field errors. Check JSON syntax, required fields and valid values. |
| 401 | Login/token missing, invalid, expired or revoked. Login again and authorize a fresh token. |
| 403 | Role lacks permission, or CSRF failed on a write. Read the error detail; these have different causes. Reload Swagger on the same hostname for CSRF. |
| 404 | The requested record/email does not exist, or a route/identifier is wrong. |
| 409 | Conflict such as a duplicate, stale edit, repeated delivery or completed rollback. Read the specific error. |
| 422 | Domain rule rejected the action, such as new care for a graduated student. |
| 503 | A required service is unavailable. Preserve the error and retry only when safe. |

The browser frontend keeps its JWT in JavaScript memory, not localStorage.
A secure HttpOnly session cookie supports session renewal. Passwords use Django
hashing. Secrets belong in ignored environment files or host secrets, never in
the showcase guide or repository.

## Verification recorded on 27 November 2026

The public site returned 200 for health/docs/schema. Independent requests with
no cookies received 401 on dashboard and students; an invalid bearer token
received 401; login without CSRF received 403; missing login fields and an
invalid recovery email received 400; an unregistered recovery email received
404. No recovery email was sent by these negative tests.

The live schema still declared localhost when inspected. The branch fix changes
only server metadata: static/runtime equality passes for all 50 paths and 77
operations. The local backend suite discovered 358 tests: 356 passed and two
PostgreSQL-only tests were skipped on SQLite. These results do not establish
that the fix is deployed, that protected live writes pass, or that a real
Registrar/Inventory gateway is integrated. Those require separate live evidence.
