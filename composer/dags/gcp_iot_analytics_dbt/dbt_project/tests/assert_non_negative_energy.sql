select *
from {{ ref('stg_iot_energy_events') }}
where energy_consumption_kwh < 0
