select
    employee_id,
    department,
    country_code,
    employee_created_at
from {{ ref('stg_employees') }}
