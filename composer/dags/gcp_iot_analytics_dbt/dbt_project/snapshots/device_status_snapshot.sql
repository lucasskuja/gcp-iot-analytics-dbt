{% snapshot device_status_snapshot %}

{{
  config(
    target_schema='snapshots',
    unique_key='device_id',
    strategy='check',
    check_cols=['status_normalized']
  )
}}

select
    device_id,
    building_id,
    status_normalized,
    event_timestamp as observed_at
from {{ ref('stg_iot_energy_events') }}
qualify row_number() over (
    partition by device_id
    order by event_timestamp desc, ingested_at desc
) = 1

{% endsnapshot %}
