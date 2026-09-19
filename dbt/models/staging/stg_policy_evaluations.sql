select
    policy_evaluation_id,
    trip_id,
    lower(policy_rule) as policy_rule,
    lower(policy_result) as policy_result,
    cast(is_material_violation as boolean) as is_material_violation,
    exception_reason,
    cast(evaluated_at as timestamp_ntz) as evaluated_at,
    cast(ingested_at as timestamp_ntz) as ingested_at
from {{ source('raw', 'raw_policy_evaluations') }}
