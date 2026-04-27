select
    max(event_timestamp) as latest_event_timestamp
from {{ ref('stg_iot_energy_events') }}
having max(event_timestamp) < timestamp_sub(current_timestamp(), interval {{ var('freshness_hours', 6) }} hour)
