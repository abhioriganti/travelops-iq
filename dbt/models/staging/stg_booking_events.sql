select
    event_id,
    session_id,
    trip_id,
    employee_id,
    lower(event_type) as event_type,
    cast(event_timestamp as timestamp_ntz) as event_timestamp,
    lower(channel) as channel,
    cast(ingested_at as timestamp_ntz) as ingested_at
from {{ source('raw', 'raw_booking_events') }}
