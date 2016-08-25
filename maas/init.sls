{%- if pillar.maas is defined %}
include:
{%- if pillar.maas.server is defined %}
- maas.server
{%- endif %}
{%- if pillar.maas.cluster is defined %}
- maas.cluster
{%- endif %}
{%- if pillar.maas.region is defined %}
- maas.region
{%- endif %}
{%- endif %}
