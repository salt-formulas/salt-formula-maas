{%- if pillar.maas is defined %}
include:
{%- if pillar.maas.cluster is defined %}
- maas.cluster
{%- endif %}
{%- if pillar.maas.mirror is defined %}
- maas.mirror
{%- endif %}
{%- if pillar.maas.region is defined %}
- maas.region
{%- endif %}
{%- endif %}
