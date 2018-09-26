{%- from "maas/map.jinja" import mirror with context %}

{%- if mirror.get('enabled') %}

{%- if mirror.get('image') %}

maas_mirror_packages:
  pkg.installed:
    - names: {{ mirror.pkgs }}

{%- for section_name, section in mirror.image.sections.iteritems() %}
{%- if pillar.maas.region is defined and pillar.maas.region.maas_config.http_proxy is defined and pillar.maas.region.maas_config.get('enable_http_proxy', False) %}
{%- set http_proxy = salt['pillar.get']('maas:region:maas_config').get('http_proxy', 'None') %}
{%- set https_proxy = salt['pillar.get']('maas:region:maas_config').get('https_proxy', 'None') %}
maas_mirror_proxy_{{ section_name }}:
  environ.setenv:
  - name: HTTP_PROXY
  - value:
      http_proxy: {{ http_proxy }}
      https_proxy: {{ https_proxy }}
  - require_in:
    - pkg: mirror_image_{{ section_name }}
{%- endif %}

mirror_image_{{ section_name }}:
  cmd.run:
  - name: "sstream-mirror --keyring={{ section.keyring }} {{ section.upstream }} {{ section.local_dir }}
    {%- if section.get('arch') %}
      'arch={{ section.arch }}'
    {%- endif %}
    {%- if section.get('filters') %}
     {% for item in section.filters %} '{{ item }}' {%- endfor %}
    {%- endif %}
    {%- if section.get('count') %}
      --max={{ section.count }}
    {%- endif %}"
  - require:
    - pkg: maas_mirror_packages

{%- endfor %}

{%- endif %}

{%- endif %}

