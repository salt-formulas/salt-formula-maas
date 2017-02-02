
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

Documentation and Bugs
======================

To learn how to install and update salt-formulas, consult the documentation
available online at:

    http://salt-formulas.readthedocs.io/

In the unfortunate event that bugs are discovered, they should be reported to
the appropriate issue tracker. Use Github issue tracker for specific salt
formula:

    https://github.com/salt-formulas/salt-formula-maas/issues

For feature requests, bug reports or blueprints affecting entire ecosystem,
use Launchpad salt-formulas project:

    https://launchpad.net/salt-formulas

You can also join salt-formulas-users team and subscribe to mailing list:

    https://launchpad.net/~salt-formulas-users

Developers wishing to work on the salt-formulas projects should always base
their work on master branch and submit pull request against specific formula.

    https://github.com/salt-formulas/salt-formula-maas

Any questions or feedback is always welcome so feel free to join our IRC
channel:

    #salt-formulas @ irc.freenode.net
