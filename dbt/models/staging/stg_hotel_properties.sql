select
    upper(cast(destination_city_code as varchar)) as destination_city_code,
    cast(destination_city_name as varchar) as destination_city_name,
    cast(place_id as varchar) as place_id,
    cast(property_name as varchar) as property_name,
    cast(formatted_address as varchar) as formatted_address,
    upper(cast(country_code as varchar)) as country_code,
    cast(property_latitude as number(9, 6)) as property_latitude,
    cast(property_longitude as number(9, 6)) as property_longitude,
    cast(distance_meters as number(10, 2)) as distance_meters,
    cast(categories as varchar) as categories,
    cast(has_website as boolean) as has_website,
    cast(source as varchar) as source,
    cast(retrieved_at as timestamp_ntz) as retrieved_at
from {{ source('raw', 'raw_hotel_properties') }}
