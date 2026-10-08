# Feature verification record — 2026-10-07

Sources checked in current Snowflake docs. Feature status may vary by cloud, edition, role and region; verify again before paid execution.

- Online Feature Store: **public preview** (July 10, 2026); Postgres-backed, stream views, REST ingest/query; 10-ms p50 is a vendor figure, not our measurement. https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/online-feature-store
- ML Jobs: documented GPU compute pool training, job submission. https://docs.snowflake.com/en/developer-guide/snowflake-ml/ml-jobs/overview
- Cortex Agent code execution: **GA announced Oct 5, 2026** (individual docs can have lagging preview banners). https://docs.snowflake.com/en/release-notes/2026/other/2026-10-05-cortex-agents-code-execution-tool-ga
- Cortex AI Function Evaluation and Optimization: **public preview Sep 21, 2026**, both billable. https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-function-studio
- Snowpipe Streaming high-performance architecture: generally available; limits and support vary. https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-limitations
- Native semantic views, secure/temp agents: available per current SQL docs. https://docs.snowflake.com/en/sql-reference/sql/create-agent
- Declarative Feature Store CLI `snow feature plan/apply`: **private preview**; no dependency on it is assumed. https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/feature-development-lifecycle

Source pages may have changes after the snapshot date. Status of every actual run must be captured in its JSON output.
