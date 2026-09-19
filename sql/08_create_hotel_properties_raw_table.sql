-- TravelOpsIQ: live external hotel-property discovery data.
-- This is a bounded Geoapify Places result set around version-controlled city
-- centers. It is not hotel availability, pricing, inventory, or booking data.

USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
USE DATABASE TRAVEL_ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS raw_hotel_properties (
    destination_city_code VARCHAR(3) NOT NULL,
    destination_city_name VARCHAR NOT NULL,
    place_id VARCHAR NOT NULL,
    property_name VARCHAR,
    formatted_address VARCHAR,
    country_code VARCHAR(2),
    property_latitude NUMBER(9, 6) NOT NULL,
    property_longitude NUMBER(9, 6) NOT NULL,
    distance_meters NUMBER(10, 2),
    categories VARCHAR,
    has_website BOOLEAN,
    source VARCHAR NOT NULL,
    retrieved_at TIMESTAMP_NTZ NOT NULL
);

SHOW TABLES LIKE 'RAW_HOTEL_PROPERTIES' IN SCHEMA RAW;
