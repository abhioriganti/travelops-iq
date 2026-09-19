select
    session_id,
    min(employee_id) as employee_id,
    min(event_timestamp) as session_started_at,
    max(event_timestamp) as session_ended_at,
    min(channel) as channel,
    max(iff(event_type = 'search_submitted', 1, 0)) as did_search,
    max(iff(event_type = 'results_viewed', 1, 0)) as did_view_results,
    max(iff(event_type = 'checkout_started', 1, 0)) as did_start_checkout,
    max(iff(event_type = 'booking_confirmed', 1, 0)) as did_book,
    max(trip_id) as trip_id
from {{ ref('stg_booking_events') }}
group by 1
