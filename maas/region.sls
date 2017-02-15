{%- from "maas/map.jinja" import region with context %}
{%- if region.enabled %}

maas_region_packages:
  pkg.installed:
    - names: {{ region.pkgs }}

/etc/maas/regiond.conf:
  file.managed:
  - source: salt://maas/files/regiond.conf
  - template: jinja
  - require:
    - pkg: maas_region_packages

{%- if region.get('enable_iframe', False)  %}

/etc/apache2/conf-enabled/maas-http.conf:
  file.managed:
  - source: salt://maas/files/maas-http.conf
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: maas_region_packages
  - require_in:
    - service: maas_region_services

maas_apache_headers:
  cmd.run:
  - name: "a2enmod headers"
  - require:
    - pkg: maas_region_packages
  - require_in:
    - service: maas_region_services

{%- endif %}

{% if region.theme is defined %}

/usr/share/maas/web/static/css/maas-styles.css:
  file.managed:
  - source: salt://maas/files/{{ region.theme }}-styles.css
  - mode: 644
  - watch_in:
    - service: maas_region_services

{%- endif %}

/etc/maas/preseeds/curtin_userdata_amd64_generic_trusty:
  file.managed:
  - source: salt://maas/files/curtin_userdata_amd64_generic_trusty
  - template: jinja
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: maas_region_packages

maas_region_services:
  service.running:
  - enable: true
  - names: {{ region.services }}
  - require:
    - cmd: maas_region_syncdb
  - watch:
    - file: /etc/maas/regiond.conf

maas_region_syncdb:
  cmd.run:
  - names:
    - maas-region syncdb
  - require:
    - file: /etc/maas/regiond.conf

maas_set_admin_password:
  cmd.run:
  - name: "maas createadmin --username {{ region.admin.username }} --password {{ region.admin.password }} --email {{ region.admin.email }} && touch /var/lib/maas/.setup_admin"
  - creates: /var/lib/maas/.setup_admin
  - require:
    - service: maas_region_services

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

maas_fabrics:
  module.run:
  - name: maas.process_fabrics
  - require:
    - cmd: maas_login_admin

maas_subnets:
  module.run:
  - name: maas.process_subnets
  - require:
    - cmd: maas_login_admin
    - module: maas_fabrics

maas_devices:
  module.run:
  - name: maas.process_devices
  - require:
    - cmd: maas_login_admin
    - module: maas_subnets

maas_machines:
  module.run:
  - name: maas.process_machines
  - require:
    - cmd: maas_login_admin
    - module: maas_subnets

maas_dhcp_snippets:
  module.run:
  - name: maas.process_dhcp_snippets
  - require:
    - cmd: maas_login_admin

maas_package_repositories:
  module.run:
  - name: maas.process_package_repositories
  - require:
    - cmd: maas_login_admin

maas_boot_resources:
  module.run:
  - name: maas.process_boot_resources
  - require:
    - cmd: maas_login_admin

{%- endif %}

