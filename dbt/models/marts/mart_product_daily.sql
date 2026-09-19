with daily_funnel as (
    select
        session_date,
        count_if(did_search = 1) as search_sessions,
        count_if(did_view_results = 1) as result_view_sessions,
        count_if(did_start_checkout = 1) as checkout_sessions,
        count_if(did_book = 1) as booked_sessions,
        count_if(did_search = 1 and did_book = 0) as abandoned_search_sessions,
        count_if(channel = 'mobile' and did_search = 1) as mobile_search_sessions,
        avg(iff(did_book = 1, session_duration_minutes, null)) as average_booked_session_minutes
    from {{ ref('fct_booking_sessions') }}
    group by 1
)

select
    session_date,
    search_sessions,
    result_view_sessions,
    checkout_sessions,
    booked_sessions,
    abandoned_search_sessions,
    round(booked_sessions / nullif(search_sessions, 0), 4) as search_to_book_conversion_rate,
    round(checkout_sessions / nullif(search_sessions, 0), 4) as search_to_checkout_rate,
    round(booked_sessions / nullif(checkout_sessions, 0), 4) as checkout_to_book_conversion_rate,
    mobile_search_sessions,
    average_booked_session_minutes
from daily_funnel
