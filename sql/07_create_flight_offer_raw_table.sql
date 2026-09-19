-- TravelOpsIQ: anonymous Duffel test-mode flight-offer snapshots.
-- This table is sandbox-only. It stores no traveler, employee, booking,
-- payment, or order data, and must not be interpreted as market pricing.

USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
USE DATABASE TRAVEL_ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS raw_flight_offer_snapshots (
    offer_request_id VARCHAR NOT NULL,
    offer_id VARCHAR NOT NULL,
    origin_iata VARCHAR(3) NOT NULL,
    destination_iata VARCHAR(3) NOT NULL,
    departure_date DATE NOT NULL,
    cabin_class VARCHAR,
    owner_iata VARCHAR(3),
    owner_name VARCHAR,
    total_amount NUMBER(12, 2),
    total_currency VARCHAR(3),
    tax_amount NUMBER(12, 2),
    tax_currency VARCHAR(3),
    segment_count INTEGER,
    stop_count INTEGER,
    journey_duration_minutes INTEGER,
    first_departing_at TIMESTAMP_NTZ,
    last_expires_at TIMESTAMP_NTZ,
    source VARCHAR NOT NULL,
    environment VARCHAR NOT NULL,
    retrieved_at TIMESTAMP_NTZ NOT NULL
);

SHOW TABLES LIKE 'RAW_FLIGHT_OFFER_SNAPSHOTS' IN SCHEMA RAW;
