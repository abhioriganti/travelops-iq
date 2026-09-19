select
    expense_id,
    trip_id,
    employee_id,
    expense_category,
    amount_usd,
    has_receipt,
    approval_status,
    submitted_at,
    cast(submitted_at as date) as submitted_date
from {{ ref('stg_expenses') }}
