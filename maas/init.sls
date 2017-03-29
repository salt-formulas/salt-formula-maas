{%- if pillar.maas is defined %}
include:
{%- if pillar.maas.region is defined %}
- maas.region
{%- endif %}
{%- if pillar.maas.machines is defined %}
- maas.machines
{%- endif %}
{%- if pillar.maas.cluster is defined %}
- maas.cluster
{%- endif %}
{%- endif %}
