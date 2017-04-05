{%- from "maas/map.jinja" import region with context %}

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

deploy_machines:
  module.run:
  - name: maas.deploy_machines
  - require:
    - cmd: maas_login_admin
