{%- from "maas/map.jinja" import cluster with context %}
{%- if cluster.enabled %}

mass_cluster_packages:
  pkg.installed:
    - names: {{ cluster.pkgs }}

{{ cluster.config.cluster }}:
  file.line:
  - content: 'maas_url: http://10.200.50.13/'
  - match: 'maas_url*'
  - mode: replace
  - location: end
  - require:
    - pkg: mass_cluster_packages

{%- endif %}
