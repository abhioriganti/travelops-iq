with trips as (
    select * from {{ ref('stg_trips') }}
),

employees as (
    select * from {{ ref('stg_employees') }}
),

policy as (
    select * from {{ ref('stg_policy_evaluations') }}
),

expenses_by_trip as (
    select
        trip_id,
        count(*) as expense_count,
        sum(amount_usd) as expense_amount_usd,
        count_if(has_receipt) as expenses_with_receipt_count,
        count_if(approval_status = 'approved') as approved_expense_count
    from {{ ref('stg_expenses') }}
    group by 1
),

support_by_trip as (
    select
        trip_id,
        count(*) as support_case_count,
        avg(datediff('hour', opened_at, resolved_at)) as average_resolution_hours
    from {{ ref('stg_support_cases') }}
    group by 1
)

select
    trips.trip_id,
    trips.employee_id,
    employees.department,
    employees.country_code,
    trips.booking_session_id,
    trips.booking_timestamp,
    trips.departure_date,
    trips.return_date,
    trips.origin_city_code,
    trips.destination_city_code,
    trips.airline_name,
    trips.hotel_chain,
    trips.booked_cost_usd,
    trips.trip_status,
    policy.policy_rule,
    policy.policy_result,
    policy.is_material_violation,
    policy.exception_reason,
    coalesce(expenses_by_trip.expense_count, 0) as expense_count,
    coalesce(expenses_by_trip.expense_amount_usd, 0) as expense_amount_usd,
    coalesce(expenses_by_trip.expenses_with_receipt_count, 0) as expenses_with_receipt_count,
    coalesce(expenses_by_trip.approved_expense_count, 0) as approved_expense_count,
    coalesce(support_by_trip.support_case_count, 0) as support_case_count,
    support_by_trip.average_resolution_hours
from trips
inner join employees on trips.employee_id = employees.employee_id
inner join policy on trips.trip_id = policy.trip_id
left join expenses_by_trip on trips.trip_id = expenses_by_trip.trip_id
left join support_by_trip on trips.trip_id = support_by_trip.trip_id
