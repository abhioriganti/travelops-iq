with properties as (
    select * from {{ ref('stg_hotel_properties') }}
)

select
    retrieved_at,
    destination_city_code,
    destination_city_name,
    country_code,
    count(*) as discovered_hotel_count,
    iff(count(*) >= 50, true, false) as is_result_limit_reached,
    count_if(property_name is not null) as named_hotel_count,
    count_if(has_website) as hotels_with_website_count,
    round(avg(distance_meters), 2) as average_distance_from_city_center_meters,
    round(min(distance_meters), 2) as nearest_property_distance_meters,
    source
from properties
group by
    retrieved_at,
    destination_city_code,
    destination_city_name,
    country_code,
    source
