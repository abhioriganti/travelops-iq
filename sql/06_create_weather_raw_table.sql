-- TravelOpsIQ: external historical-weather landing table.
-- Run as TRAVEL_ANALYTICS_DEV after the base RAW tables exist.
-- This table stores public Open-Meteo observations only; it contains no
-- employee, trip, booking, expense, or support identifiers.

USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
USE DATABASE TRAVEL_ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS raw_weather_observations (
    location_code VARCHAR NOT NULL,
    location_name VARCHAR NOT NULL,
    country_code VARCHAR NOT NULL,
    weather_date DATE NOT NULL,
    latitude NUMBER(9, 6) NOT NULL,
    longitude NUMBER(9, 6) NOT NULL,
    temperature_max_c NUMBER(6, 2),
    precipitation_sum_mm NUMBER(8, 2),
    wind_speed_max_kmh NUMBER(7, 2),
    weather_code INTEGER,
    source VARCHAR NOT NULL,
    retrieved_at TIMESTAMP_NTZ NOT NULL
);

SHOW TABLES LIKE 'RAW_WEATHER_OBSERVATIONS' IN SCHEMA RAW;
