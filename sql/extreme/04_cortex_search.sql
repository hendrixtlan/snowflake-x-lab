-- LIVE: Create an indexed semantic retrieval service (ongoing credit consumption).
CREATE TABLE IF NOT EXISTS MUSIC_LAB.AI.CONTENT_DOCS (
  TENANT_ID VARCHAR NOT NULL, CONTENT_ID VARCHAR NOT NULL,
  TITLE VARCHAR, DESCRIPTION VARCHAR
);
CREATE OR REPLACE CORTEX SEARCH SERVICE MUSIC_LAB.AI.CONTENT_SEARCH
 ON DESCRIPTION
 ATTRIBUTES TENANT_ID
 WAREHOUSE = MUSIC_LAB_XS
 TARGET_LAG = '1 hour'
 AS SELECT TENANT_ID, CONTENT_ID, TITLE, DESCRIPTION
    FROM MUSIC_LAB.AI.CONTENT_DOCS
    WHERE TENANT_ID = 't1';
-- SECURITY CRITICAL: Cortex Search filtering must be enforced by trusted application code
-- and/or separate tenant-specific services. Agent instructions alone are not isolation.

-- For each additional tenant, provision a separately scoped search service and
-- matching agent with grants restricted to that tenant's role. Do not reuse
-- this t1-only service across tenants or rely on prompt text for filtering.
