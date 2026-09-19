select
    employee_id,
    department,
    country_code,
    cast(employee_created_at as timestamp_ntz) as employee_created_at,
    cast(ingested_at as timestamp_ntz) as ingested_at
from {{ source('raw', 'raw_employees') }}
