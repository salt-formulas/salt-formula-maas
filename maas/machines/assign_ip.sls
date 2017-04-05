{%- from "maas/map.jinja" import region with context %}

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

assign_ips_to_machines:
  module.run:
  - name: maas.process_assign_machines_ip
  - require:
    - cmd: maas_login_admin
