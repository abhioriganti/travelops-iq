-- Lesson 4: local development identity for dbt.
-- Run as ACCOUNTADMIN in the SAME trial account where TRAVEL_ANALYTICS exists.
-- Replace the password placeholder before running. Do not save, share, or commit it.

USE ROLE ACCOUNTADMIN;

CREATE USER IF NOT EXISTS TRAVEL_ANALYTICS_DBT
  LOGIN_NAME = 'TRAVEL_ANALYTICS_DBT'
  DISPLAY_NAME = 'Travel Analytics dbt local developer'
  PASSWORD = '<REPLACE_WITH_A_NEW_LONG_UNIQUE_PASSWORD>'
  MUST_CHANGE_PASSWORD = FALSE
  DEFAULT_ROLE = TRAVEL_ANALYTICS_DEV
  DEFAULT_WAREHOUSE = TRAVEL_ANALYTICS_XS
  DEFAULT_NAMESPACE = 'TRAVEL_ANALYTICS.DBT_DEV'
  COMMENT = 'Local-only dbt identity for the Travel Operations Analytics Lab';

GRANT ROLE TRAVEL_ANALYTICS_DEV TO USER TRAVEL_ANALYTICS_DBT;

-- Verify the user was created. Do not include the password in this query.
SHOW USERS LIKE 'TRAVEL_ANALYTICS_DBT';
