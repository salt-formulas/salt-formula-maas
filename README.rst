
==================
Metal as a Service
==================

Service maas description

Sample pillars
==============

Single maas service

.. code-block:: yaml

    maas:
      server:
        enabled: true

Single MAAS region service [single UI/API]

.. code-block:: yaml

    maas:
      region:
        enabled: true
        bind:
          host: localhost
          port: 80
        database:
          engine: postgresql
          host: localhost
          name: maasdb
          password: password
          username: maas


Single MAAS cluster service [multiple racks]

.. code-block:: yaml

    maas:
      cluster:
        enabled: true
        version: '2'
        region: 
          host: localhost
          port: 5240



Read more
=========

* 
