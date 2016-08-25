{%- from "maas/map.jinja" import cluster with context %}
{%- if cluster.enabled %}

maas_cluster_packages:
  pkg.installed:
    - names: {{ cluster.pkgs }}

{{ cluster.config.cluster }}:
  file.line:
  - content: 'maas_url: {{ cluster.region.host }}:{{ cluster.region.port }}'
  - match: 'maas_url*'
  - mode: replace
  - location: end
  - require:
    - pkg: maas_cluster_packages

{%- endif %}
