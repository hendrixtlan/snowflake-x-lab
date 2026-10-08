-- LIVE: Native semantic view, not a text-only YAML imitation.
CREATE OR REPLACE SEMANTIC VIEW MUSIC_LAB.AI.ENGAGEMENT_SEMANTICS
 TABLES (engagement AS MUSIC_LAB.GOVERNANCE.AUTHORIZED_USER_COUNTS)
 DIMENSIONS (
   engagement.tenant AS engagement.TENANT_ID,
   engagement.listener AS engagement.USER_ID
 )
 METRICS (
   engagement.total_plays AS SUM(engagement.LISTENS),
   engagement.active_listeners AS COUNT(DISTINCT engagement.USER_ID)
 )
 AI_SQL_GENERATION 'Tenant isolation must be enforced with database row access policies and caller privileges, not just prompt instructions.';
