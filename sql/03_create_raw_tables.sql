-- Lesson 6: raw source landing tables.
-- The first two statements are a one-time, RAW-schema-only permission grant.
-- The remaining statements run as TRAVEL_ANALYTICS_DEV using TRAVEL_ANALYTICS_XS.
-- These tables retain source-shaped fields; dbt will clean and model them later.

USE ROLE ACCOUNTADMIN;
GRANT CREATE STAGE, CREATE FILE FORMAT ON SCHEMA TRAVEL_ANALYTICS.RAW TO ROLE TRAVEL_ANALYTICS_DEV;

USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
USE DATABASE TRAVEL_ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS raw_employees (
    employee_id VARCHAR NOT NULL,
    department VARCHAR NOT NULL,
    country_code VARCHAR NOT NULL,
    employee_created_at TIMESTAMP_NTZ NOT NULL,
    ingested_at TIMESTAMP_NTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_trips (
    trip_id VARCHAR NOT NULL,
    employee_id VARCHAR NOT NULL,
    booking_session_id VARCHAR NOT NULL,
    booking_timestamp TIMESTAMP_NTZ NOT NULL,
    departure_date DATE NOT NULL,
    return_date DATE NOT NULL,
    origin_city_code VARCHAR NOT NULL,
    destination_city_code VARCHAR NOT NULL,
    airline_name VARCHAR NOT NULL,
    hotel_chain VARCHAR NOT NULL,
    booked_cost_usd NUMBER(12, 2) NOT NULL,
    trip_status VARCHAR NOT NULL,
    ingested_at TIMESTAMP_NTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_booking_events (
    event_id VARCHAR NOT NULL,
    session_id VARCHAR NOT NULL,
    trip_id VARCHAR,
    employee_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    event_timestamp TIMESTAMP_NTZ NOT NULL,
    channel VARCHAR NOT NULL,
    ingested_at TIMESTAMP_NTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_expenses (
    expense_id VARCHAR NOT NULL,
    trip_id VARCHAR NOT NULL,
    employee_id VARCHAR NOT NULL,
    expense_category VARCHAR NOT NULL,
    amount_usd NUMBER(12, 2) NOT NULL,
    has_receipt BOOLEAN NOT NULL,
    approval_status VARCHAR NOT NULL,
    submitted_at TIMESTAMP_NTZ NOT NULL,
    ingested_at TIMESTAMP_NTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_policy_evaluations (
    policy_evaluation_id VARCHAR NOT NULL,
    trip_id VARCHAR NOT NULL,
    policy_rule VARCHAR NOT NULL,
    policy_result VARCHAR NOT NULL,
    is_material_violation BOOLEAN NOT NULL,
    exception_reason VARCHAR,
    evaluated_at TIMESTAMP_NTZ NOT NULL,
    ingested_at TIMESTAMP_NTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_support_cases (
    support_case_id VARCHAR NOT NULL,
    trip_id VARCHAR NOT NULL,
    issue_type VARCHAR NOT NULL,
    opened_at TIMESTAMP_NTZ NOT NULL,
    resolved_at TIMESTAMP_NTZ NOT NULL,
    resolution_channel VARCHAR NOT NULL,
    ingested_at TIMESTAMP_NTZ NOT NULL
);

SHOW TABLES IN SCHEMA RAW;
