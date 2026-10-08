-- SECURITY CRITICAL: execute LAST, after granting dedicated roles and testing identities.
-- Principal mappings are maintained by authorized administrators, not user-supplied prompts.
CREATE TABLE IF NOT EXISTS MUSIC_LAB.GOVERNANCE.PRINCIPAL_TENANTS (
  PRINCIPAL_NAME VARCHAR NOT NULL,
  TENANT_ID VARCHAR NOT NULL
);
CREATE OR REPLACE ROW ACCESS POLICY MUSIC_LAB.GOVERNANCE.TENANT_RAP
 AS (row_tenant_id VARCHAR) RETURNS BOOLEAN ->
 EXISTS (
   SELECT 1 FROM MUSIC_LAB.GOVERNANCE.PRINCIPAL_TENANTS memberships
   WHERE memberships.PRINCIPAL_NAME = CURRENT_USER()
     AND memberships.TENANT_ID = row_tenant_id
 );
-- Only attach after inserting controlled user mappings and verifying policy-owner grants.
-- ALTER TABLE MUSIC_LAB.STREAM.EVENTS ADD ROW ACCESS POLICY
-- MUSIC_LAB.GOVERNANCE.TENANT_RAP ON (TENANT_ID);
-- The policy owner requires access to the mapping table. Agent/SERVICE roles MUST
-- be validated for caller-vs-owner security semantics; no shared system-user bypass.

-- Fully-qualified principal-scoped view: CREATE this before semantic view (03).
CREATE OR REPLACE SECURE VIEW MUSIC_LAB.GOVERNANCE.AUTHORIZED_USER_COUNTS AS
 SELECT counts.* FROM MUSIC_LAB.FEATURES.DT_USER_COUNTS counts
 WHERE EXISTS (SELECT 1 FROM MUSIC_LAB.GOVERNANCE.PRINCIPAL_TENANTS m
   WHERE m.PRINCIPAL_NAME = CURRENT_USER() AND m.TENANT_ID = counts.TENANT_ID);
-- Restrict grants on membership table and on all raw/unrestricted feature tables.
-- The analyst semantic view points to the SECURE VIEW, not the base dynamic table.
