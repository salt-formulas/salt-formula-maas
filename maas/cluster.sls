{%- from "maas/map.jinja" import cluster with context %}
{%- if cluster.enabled %}

{%- if cluster.role == 'slave' %}

maas_cluster_remove_secrets:
  cmd.run:
  - name: "rm -f /var/lib/maas/maas_id /var/lib/maas/secret && touch /var/lib/maas/.cluster_bootstrap_secrets"
  - creates: /var/lib/maas/.cluster_bootstrap_secrets
  - watch_in:
    - service: maas_region_services
  - require:
    - pkg: maas_region_packages

maas_cluster_dns_conflicts:
  cmd.run:
  - name: "maas-region edit_named_options --migrate-conflicting-options && touch /var/lib/maas/.cluster_bootstrap_dns"
  - creates: /var/lib/maas/.cluster_bootstrap_dns
  - watch_in:
    - service: maas_region_services
  - require:
    - pkg: maas_region_packages

{%- endif %}

{%- endif %}
