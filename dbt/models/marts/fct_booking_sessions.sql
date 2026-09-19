select
    session_id,
    employee_id,
    trip_id,
    session_started_at,
    cast(session_started_at as date) as session_date,
    session_ended_at,
    datediff('minute', session_started_at, session_ended_at) as session_duration_minutes,
    channel,
    did_search,
    did_view_results,
    did_start_checkout,
    did_book,
    iff(did_search = 1 and did_book = 0, true, false) as is_abandoned_after_search
from {{ ref('int_booking_funnel_sessions') }}
