-- CLOUD GATED. Cost incurred after execution. Dev account ONLY.
-- Prerequisite: a role permitted to create database, warehouse, schemas and stages.
-- Change name to a dedicated isolated DB for real evaluations.
CREATE DATABASE IF NOT EXISTS MUSIC_LAB;
CREATE SCHEMA IF NOT EXISTS MUSIC_LAB.STREAM;
CREATE SCHEMA IF NOT EXISTS MUSIC_LAB.AI;
CREATE SCHEMA IF NOT EXISTS MUSIC_LAB.GOVERNANCE;
CREATE SCHEMA IF NOT EXISTS MUSIC_LAB.EXPERIMENTS;
CREATE WAREHOUSE IF NOT EXISTS MUSIC_LAB_XS
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;
-- Snowflake account budgets / resource monitors / Cortex quotas must be set
-- by an authorized administrator BEFORE creating continuously billed services.
