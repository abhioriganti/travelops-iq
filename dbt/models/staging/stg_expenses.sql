select
    expense_id,
    trip_id,
    employee_id,
    lower(expense_category) as expense_category,
    cast(amount_usd as number(12, 2)) as amount_usd,
    cast(has_receipt as boolean) as has_receipt,
    lower(approval_status) as approval_status,
    cast(submitted_at as timestamp_ntz) as submitted_at,
    cast(ingested_at as timestamp_ntz) as ingested_at
from {{ source('raw', 'raw_expenses') }}
