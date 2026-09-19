select
    trip_id,
    employee_id,
    booking_session_id,
    cast(booking_timestamp as timestamp_ntz) as booking_timestamp,
    cast(departure_date as date) as departure_date,
    cast(return_date as date) as return_date,
    origin_city_code,
    destination_city_code,
    airline_name,
    hotel_chain,
    cast(booked_cost_usd as number(12, 2)) as booked_cost_usd,
    lower(trip_status) as trip_status,
    cast(ingested_at as timestamp_ntz) as ingested_at
from {{ source('raw', 'raw_trips') }}
