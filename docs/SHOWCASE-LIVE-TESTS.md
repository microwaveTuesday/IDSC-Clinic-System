# Hosted showcase verification: 27-28 November 2026

The public Clinic was tested with explicitly fictional `SHOWCASE-*` records.
These results distinguish live checks from isolated CI tests and remaining
requirements. They do not claim a real Registrar/Inventory gateway connection.

## Deployed revision and Swagger

- Website: <https://idsc-clinic-management.vercel.app>
- Swagger: <https://idsc-clinic-management.vercel.app/docs>
- Released revision: `a6d58533bcf283414bcc7cb0cc497d135af036b9`.
- [Main release run 45954207664](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/45954207664)
  passed the 12 quality jobs and production release on attempt 2. The first
  attempt stopped on a staged frontend 404; the approved retry passed staging,
  promotion and the public checks. No failed smoke check was bypassed.
- The schema now declares `/` as its server. Live Swagger **Try it out** called
  the public HTTPS `/health` and returned 200. A session-issued JWT entered into
  **bearerAuth** produced a real Bearer header and 200 on the Dashboard.
- Tokens and passwords were excluded from public evidence. See
  [SWAGGER-AUTHORIZATION.md](SWAGGER-AUTHORIZATION.md) for the exact steps.

## Fresh setup and retained fixtures

At the operator's request, a new snapshot-consistent private PostgreSQL backup
was made and its custom archive listing verified. The 15 scoped application
tables were cleared, preserving migrations, role definitions and schema. The
operator registered the fresh single Owner. Registration then closed, and zero
accounts other than Owner and zero clinical/provider rows were verified before
test fixtures were added.

The operator requested retaining named fixtures for rehearsal. Current fixtures
include `SHOWCASE-001` (active), `SHOWCASE-002` (graduated), `SHOWCASE-003`
(dropped out), `SHOWCASE-MED-001`, and eleven `showcase_staff_*` accounts.
Known synthetic login details are kept privately under ignored `.runtime/`;
they are not included in the report or repository.

Corrected private Owner access was supplied later on 28 November. The orphan
first Staff fixture was deleted and recreated through the authorized API;
all eleven retained Staff and one retained rehearsal Admin now have privately
saved login details. The Owner's credentials were not changed by the tests.

## Executed live checks

The sanitized protected ledger currently contains 193 HTTP/behavior checks:
191 successful results and two unexpected results described below. This is a
mixed ledger of requests and assertions, not 193 independent test cases.
Nine separate public/security checks also passed.

| Area | Observed result |
| --- | --- |
| Public/API errors | Health 200; anonymous protected reads and invalid bearer 401; missing CSRF 403; validation 400; unknown recovery email 404 |
| Registrar simulation | ID-only lookup, duplicate rejection, missing ID, profile edit reflected in Clinic |
| Enrollment | GRADUATED and DROPPED_OUT rejected new health records, consultations, health statuses and dispensing with 422 |
| Clinical records | Create/read/edit; Owner deletion of own temporary rows; deleted-ID 404; Staff deletion 403 |
| Stock | Dispense reduced stock once; insufficient stock and zero quantity rejected; rollback restored stock once |
| Restocks | Selected and ALL requests, pending stock unchanged, fulfillment increased stock, duplicate delivery rejected |
| Reports | All four report endpoints returned 200 |
| Staff roles | Clinic access allowed; Staff/Admin directories and Owner-only mock workspaces returned 403 for Staff |
| Account lifecycle | Owner created/edited/deactivated/reactivated synthetic Staff; old JWT failed after deactivation; fresh login worked after activation |
| Pagination | Eleven Staff split ten plus one; requested page size 100 was capped to ten; live UI boundary controls/search reset checked |
| Password/username | Synthetic Staff mismatch/weak-password 400; valid rotation 200; old password/JWT 401; current session retained; own username changed and restored |
| Reliability | Current timestamp edit 200, stale timestamp 409; same-key dispense/rollback replayed without duplicate stock changes; changed payload/key reuse 409; logout revoked JWT |
| Database | Fictional rows created on 27 November remained in PostgreSQL on 28 November; the new live UI allergy edit was read directly from its database row |
| Live UI | Lookup error/recovery, minimum-height validation, saved edit, delete Cancel, graduated/dropped-out disabled controls, ten-plus-one pagination |
| Phone width | Dashboard, Students, Medicine stock and Administration had 375px document width inside a 390px viewport; no document-level horizontal overflow |

## Unexpected results and remaining checks

1. The earlier private Owner login returned 401. Corrected private access later
   returned 200 with role OWNER. An additional, separate ledger of 83 live
   Owner/Admin/account checks then passed: five-Admin capacity, inactive Admins
   counting toward the limit, deletion freeing a slot, Owner Admin lifecycle,
   Admin Staff lifecycle, wrong-password deletion rejection, account deletion
   preserving clinical records, revoked sessions, and Admin clinical/history
   deletion. Only named synthetic fixtures were changed. Extra limit-test
   Admins were removed; one Admin and eleven Staff remain for rehearsal.
2. The hosted proxy weakened an ETag (`W/`), so using it as a strong `If-Match`
   precondition returned 409. The existing `X-Record-Version` header, copied from
   the latest `updated_at`, passed both current and stale-version checks.
   Do not treat a weak ETag as a strong representation validator.

Eight additional live Staff UI checks passed: Administration/mock menus and
clinical/history delete controls were absent; normal clinic features remained
available. The Owner session was restored afterward. The main 193-entry ledger
retains its original results rather than rewriting the earlier failed attempt.

Still unverified live: full hosted reset email-link redemption. Prior inbox
receipt/opening and isolated CI password recovery do not establish completed
hosted redemption.

Real provider gateway and partner-offline tests need the other groups' finished
API/agreements. Exact shared class/Figma and peer-module UI conformity need
their references. These requirements are not replaced by mock workspaces.

## Follow-up corrections from this verification

The original Dashboard notice incorrectly said all business data resets on a
restart. The prepared wording limits that statement to demonstration student
and medicine data. Clinic records/accounts are database-backed in this hosting
profile. Registrar/Inventory mocks were observed resetting and the same
fictional IDs were restored for rehearsal; that restoration is not evidence
that provider data persisted.

The committed OpenAPI also differed from the live PostgreSQL schema in four
medicine quantity range/format entries. DRF inferred a 64-bit limit on SQLite
and a 32-bit limit on PostgreSQL. The serializer now explicitly uses the
deployed PostgreSQL `PositiveIntegerField` maximum, 2,147,483,647. The corrected
merged `openapi.yaml` exactly equals the live schema: 50 paths / 77 operations.
No routes or request/response field names were changed, and no migration is
required. Regression tests check the portable range and both request/response
schema entries on each CI database.

The approved PR10 release passed all 12 quality jobs but stopped at the staged
frontend's initial HTTP 404 before promotion. The same address subsequently
loaded the Clinic login page. See [STAGING-READINESS.md](STAGING-READINESS.md)
for the bounded-readiness correction; a new successful production release is
still required before claiming the corrected notice is published.
