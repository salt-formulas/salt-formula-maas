{%- from "maas/map.jinja" import cluster with context %}
{%- if cluster.get('enabled', False) %}

{%- if cluster.role == 'slave' %}

maas_cluster_remove_secrets:
  cmd.run:
  - name: "rm -f /var/lib/maas/maas_id /var/lib/maas/secret && touch /var/lib/maas/.cluster_bootstrap_secrets"
  - creates: /var/lib/maas/.cluster_bootstrap_secrets
  - watch_in:
    - service: maas_region_services
  - require:
    - pkg: maas_region_packages
  - require_in:
    - pkg: maas_cluster_packages

maas_cluster_dns_conflicts:
  cmd.run:
  - name: "maas-region edit_named_options --migrate-conflicting-options && touch /var/lib/maas/.cluster_bootstrap_dns"
  - creates: /var/lib/maas/.cluster_bootstrap_dns
  - watch_in:
    - service: maas_region_services
  - require:
    - pkg: maas_region_packages
  - require_in:
    - pkg: maas_cluster_packages

maas_setup_admin:
  cmd.run:
  - name: "touch /var/lib/maas/.setup_admin"
  - creates: /var/lib/maas/.setup_admin
  - require:
    - pkg: maas_region_packages

{%- endif %}

maas_cluster_packages:
  pkg.installed:
    - names: {{ cluster.pkgs }}

/etc/maas/rackd.conf:
  file.line:
{%- if cluster.region.get('port', False)  %}
  {%- set maas_url = 'http://' + cluster.region.host|string + ':' + cluster.region.port|string + '/MAAS' -%}
{%- else %}
  {%- set maas_url = 'http://' + cluster.region.host|string + '/MAAS' -%}
{%- endif %}
  - content: "maas_url: {{ maas_url }}"
  - match: 'maas_url*'
  - mode: replace
  - location: end
  - require:
    - pkg: maas_cluster_packages

# salt.states.file.line doesn't support setting owner/group in Salt version 2016.3.6
# Starting from version 2016.11.0 we may remove code below and set owner/group in file.line
/etc/maas/rackd_conf:
  file.managed:
  - name: /etc/maas/rackd.conf
  - group: maas

maas_cluster_services:
  service.running:
  - enable: true
  - names: {{ cluster.services }}
  - require:
    - file: /etc/maas/rackd.conf
  - watch:
    - file: /etc/maas/rackd.conf
  {%- if grains.get('kitchen-test') %}
  - onlyif: /bin/false
  {%- endif %}

{%- endif %}
