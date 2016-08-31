
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
        theme: theme
        bind:
          host: localhost
          port: 80
        admin:
          username: admin
          password: password
          email:  email@example.com
        database:
          engine: postgresql
          host: localhost
          name: maasdb
          password: password
          username: maas
        enabled: true



Single MAAS cluster service [multiple racks]

.. code-block:: yaml

    maas:
      cluster:
        enabled: true
        role: master/slave

Read more
=========

* 
