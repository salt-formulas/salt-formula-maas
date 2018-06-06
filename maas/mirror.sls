{%- from "maas/map.jinja" import mirror with context %}

{%- if mirror.get('enabled') %}

{%- if mirror.get('image') %}

maas_mirror_packages:
  pkg.installed:
    - names: {{ mirror.pkgs }}

{%- for section_name, section in mirror.image.sections.iteritems() %}

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

