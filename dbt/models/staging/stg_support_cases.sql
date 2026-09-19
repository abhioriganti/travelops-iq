select
    support_case_id,
    trip_id,
    lower(issue_type) as issue_type,
    cast(opened_at as timestamp_ntz) as opened_at,
    cast(resolved_at as timestamp_ntz) as resolved_at,
    lower(resolution_channel) as resolution_channel,
    cast(ingested_at as timestamp_ntz) as ingested_at
from {{ source('raw', 'raw_support_cases') }}
