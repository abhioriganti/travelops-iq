with trips as (
    select * from {{ ref('fct_trips') }}
),

weather as (
    select * from {{ ref('stg_weather_observations') }}
),

trips_with_weather as (
    select
        trips.departure_date,
        trips.trip_id,
        trips.booked_cost_usd,
        weather.location_code as destination_city_code,
        weather.temperature_max_c,
        weather.precipitation_sum_mm,
        weather.wind_speed_max_kmh,
        weather.weather_code,
        weather.weather_risk_level
    from trips
    inner join weather
        on trips.destination_city_code = weather.location_code
        and trips.departure_date = weather.weather_date
),

daily_weather_risk as (
    select
        departure_date,
        count(*) as trips_with_destination_weather,
        count_if(weather_risk_level = 'high') as high_risk_trips,
        count_if(weather_risk_level = 'medium') as medium_risk_trips,
        count_if(weather_risk_level = 'low') as low_risk_trips,
        avg(temperature_max_c) as average_destination_temperature_max_c,
        avg(precipitation_sum_mm) as average_destination_precipitation_mm,
        max(wind_speed_max_kmh) as max_destination_wind_speed_kmh,
        sum(
            iff(weather_risk_level in ('high', 'medium'), booked_cost_usd, 0)
        ) as gross_booking_value_weather_exposed_usd
    from trips_with_weather
    group by 1
)

select
    departure_date,
    trips_with_destination_weather,
    high_risk_trips,
    medium_risk_trips,
    low_risk_trips,
    round(
        (high_risk_trips + medium_risk_trips)
        / nullif(trips_with_destination_weather, 0),
        4
    ) as weather_impacted_trip_rate,
    average_destination_temperature_max_c,
    average_destination_precipitation_mm,
    max_destination_wind_speed_kmh,
    gross_booking_value_weather_exposed_usd
from daily_weather_risk
