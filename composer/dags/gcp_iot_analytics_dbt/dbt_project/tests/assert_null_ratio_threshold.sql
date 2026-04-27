select *
from {{ ref('int_device_daily_quality') }}
where null_ratio > 0.15
