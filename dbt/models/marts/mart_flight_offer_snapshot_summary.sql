with offers as (
    select * from {{ ref('stg_flight_offer_snapshots') }}
)

select
    retrieved_at,
    origin_iata,
    destination_iata,
    departure_date,
    cabin_class,
    total_currency,
    count(*) as offer_count,
    count_if(stop_count = 0) as nonstop_offer_count,
    count(distinct owner_iata) as distinct_carrier_count,
    min(total_amount) as lowest_offer_amount,
    avg(total_amount) as average_offer_amount,
    max(total_amount) as highest_offer_amount,
    min(journey_duration_minutes) as shortest_journey_minutes,
    min_by(owner_name, total_amount) as lowest_offer_owner_name,
    min_by(owner_iata, total_amount) as lowest_offer_owner_iata,
    source,
    environment
from offers
group by 1, 2, 3, 4, 5, 6, 16, 17
