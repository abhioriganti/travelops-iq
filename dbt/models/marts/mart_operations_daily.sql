with daily_operations as (
    select
        booking_date,
        count(*) as booked_trips,
        count_if(is_completed) as completed_trips,
        count_if(is_cancelled) as cancelled_trips,
        sum(booked_cost_usd) as gross_booking_value_usd,
        count_if(is_in_policy) as in_policy_trips,
        sum(iff(not is_in_policy, booked_cost_usd, 0)) as out_of_policy_spend_usd,
        count_if(has_support_case) as trips_with_support_contact,
        avg(average_resolution_hours) as average_support_resolution_hours,
        sum(expense_amount_usd) as trip_linked_expense_amount_usd,
        sum(expenses_with_receipt_count) as expenses_with_receipt_count,
        sum(expense_count) as expense_count
    from {{ ref('fct_trips') }}
    group by 1
)

select
    booking_date,
    booked_trips,
    completed_trips,
    cancelled_trips,
    gross_booking_value_usd,
    in_policy_trips,
    round(in_policy_trips / nullif(booked_trips, 0), 4) as in_policy_booking_rate,
    out_of_policy_spend_usd,
    trips_with_support_contact,
    round(trips_with_support_contact / nullif(booked_trips, 0), 4) as support_contact_rate,
    average_support_resolution_hours,
    trip_linked_expense_amount_usd,
    expenses_with_receipt_count / nullif(expense_count, 0) as expense_receipt_capture_rate
from daily_operations
