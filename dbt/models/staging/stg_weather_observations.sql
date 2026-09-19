select
    upper(location_code) as location_code,
    location_name,
    country_code,
    cast(weather_date as date) as weather_date,
    cast(latitude as number(9, 6)) as latitude,
    cast(longitude as number(9, 6)) as longitude,
    cast(temperature_max_c as number(6, 2)) as temperature_max_c,
    cast(precipitation_sum_mm as number(8, 2)) as precipitation_sum_mm,
    cast(wind_speed_max_kmh as number(7, 2)) as wind_speed_max_kmh,
    cast(weather_code as integer) as weather_code,
    case
        when weather_code in (66, 67, 75, 77, 82, 85, 86, 95, 96, 99)
            or wind_speed_max_kmh >= 50
            or precipitation_sum_mm >= 15
            then 'high'
        when weather_code in (51, 53, 55, 56, 57, 61, 63, 65, 71, 73, 80, 81)
            or wind_speed_max_kmh >= 35
            or precipitation_sum_mm >= 5
            then 'medium'
        else 'low'
    end as weather_risk_level,
    cast(source as varchar) as source,
    cast(retrieved_at as timestamp_ntz) as retrieved_at
from {{ source('raw', 'raw_weather_observations') }}
