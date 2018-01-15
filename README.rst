
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
    salt_master_ip: 192.168.0.10
    region:
      upstream_proxy:
        address: 10.0.0.1
        port: 8080
        user: username      #OPTIONAL
        password: password  #OPTIONAL
      theme: mirantis
      bind:
        host: 192.168.0.10:5240
        port: 5240
      admin:
        username: exampleuser
        password: examplepassword
        email:  email@example.com
      database:
        engine: null
        host: localhost
        name: maasdb
        password: qwqwqw
        username: maas
      enabled: true
      user: mirantis
      token: "89EgtWkX45ddjMYpuL:SqVjxFG87Dr6kVf4Wp:5WLfbUgmm9XQtJxm3V2LUUy7bpCmqmnk"
      fabrics:
        test-fabric1:
          description: "Test fabric"
        test-fabric2:
          description: "Test fabric2"
      subnets:
        subnet1:
          fabric: test-fabric1
          cidr: 2.2.3.0/24
          gateway_ip: 2.2.3.2
          iprange: # reserved range for DHCP\auto mapping
            start: 2.2.3.20
            end: 2.2.3.250
      dhcp_snippets:
        test-snippet:
          value: option bootfile-name "tftp://192.168.0.10/snippet";
          description: Test snippet
          enabled: true
          subnet: subnet1
      boot_resources:
        bootscript1:
          title: bootscript
          architecture: amd64/generic
          filetype: tgz
          content: /srv/salt/reclass/nodes/path_to_file
      package_repositories:
        Saltstack:
          url: http://repo.saltstack.com/apt/ubuntu/14.04/amd64/2016.3/
          distributions:
               - trusty
          components:
              - main
          arches: amd64
          key: "-----BEGIN PGP PUBLIC KEY BLOCK-----
               Version: GnuPG v2

               mQENBFOpvpgBCADkP656H41i8fpplEEB8IeLhugyC2rTEwwSclb8tQNYtUiGdna9
                ......
               fuBmScum8uQTrEF5+Um5zkwC7EXTdH1co/+/V/fpOtxIg4XO4kcugZefVm5ERfVS
               MA==
               =dtMN
               -----END PGP PUBLIC KEY BLOCK-----"
          enabled: true
      machines:
        machine1_new_schema:
          pxe_interface_mac: "11:22:33:44:55:66" # Node will be identified by those mac
          interfaces:
            nic01: # could be any, used for iterate only
              type: eth # NotImplemented
              name: eth0 # Override default nic name. Interface to rename will be identified by mac
              mac: "11:22:33:44:55:66"
              mode: "static"
              ip: "2.2.3.19"  # ip should be out of reserved subnet range, but still in subnet range
              subnet: "subnet1"
              gateway: "2.2.3.2" # override default gateway from subnet
            nic02:
              type: eth # Not-implemented
              mac: "11:22:33:44:55:78"
              subnet: "subnet2"
              mode: "dhcp"
          power_parameters:
            power_type: ipmi
            power_address: '192.168.10.10'
            power_user: bmc_user
            power_password: bmc_password
            #Optional (for legacy HW)
            power_driver: LAN
          distro_series: xenial
          hwe_kernel: hwe-16.04
        machine1_old_schema:
          interface:
              mac: "11:22:33:44:55:88"  # Node will be identified by those mac
              mode: "static"
              ip: "2.2.3.15"
              subnet: "subnet1"
              gateway: "2.2.3.2"
          power_parameters:
            power_type: ipmi
            power_address: '192.168.10.10'
            power_user: bmc_user
            power_password: bmc_password
            #Optional (for legacy HW)
            power_driver: LAN
            # FIXME: that's should be moved into another,livirt example.
            # Used in case of power_type: virsh
            power_id: my_libvirt_vm_name
          distro_series: xenial
          hwe_kernel: hwe-16.04
      devices:
        machine1-ipmi:
          interface:
            ip_address: 192.168.10.10
            subnet: cidr:192.168.10.0/24
          mac: '66:55:44:33:22:11'
      commissioning_scripts:
        00-maas-05-simplify-network-interfaces: /etc/maas/files/commisioning_scripts/00-maas-05-simplify-network-interfaces
      maas_config:
        domain: mydomain.local
        http_proxy: http://192.168.0.10:3142
        commissioning_distro_series: xenial
        default_distro_series: xenial
        default_osystem: 'ubuntu'
        default_storage_layout: lvm
        disk_erase_with_secure_erase: true
        dnssec_validation: 'no'
        enable_third_party_drivers: true
        maas_name: cfg01
        network_discovery: 'enabled'
        active_discovery_interval: '600'
        ntp_external_only: true
        ntp_servers: 10.10.11.23 10.10.11.24
        upstream_dns: 192.168.12.13
        enable_http_proxy: true
        default_min_hwe_kernel: ''
       sshprefs:
        - 'ssh-rsa ASD.........dfsadf blah@blah'



Usage of local repos

.. code-block:: yaml

  maas:
    cluster:
      enabled: true
      region:
        port: 80
        host: localhost
      saltstack_repo_key: |
        -----BEGIN PGP PUBLIC KEY BLOCK-----
        Version: GnuPG v2

        mQENBFOpvpgBCADkP656H41i8fpplEEB8IeLhugyC2rTEwwSclb8tQNYtUiGdna9
        .....
        fuBmScum8uQTrEF5+Um5zkwC7EXTdH1co/+/V/fpOtxIg4XO4kcugZefVm5ERfVS
        MA==
        =dtMN
        -----END PGP PUBLIC KEY BLOCK-----
      saltstack_repo_xenial: "http://${_param:local_repo_url}/ubuntu-xenial stable salt"
      saltstack_repo_trusty: "http://${_param:local_repo_url}/ubuntu-trusty stable salt"

Single MAAS cluster service [multiple racks]

.. code-block:: yaml

    maas:
      cluster:
        enabled: true
        role: master/slave

.. code-block:: yaml

    maas:
      cluster:
        enabled: true
        role: master/slave

MAAS region service with backup data

.. code-block:: yaml
    maas:
      region:
        database:
          initial_data:
            source: cfg01.local
            host: 192.168.0.11

Module function's example:
==========================

* Wait for status of selected machine's:

.. code-block:: bash

    > cat maas/machines/wait_for_machines_ready.sls

    ...

    wait_for_machines_ready:
      module.run:
      - name: maas.wait_for_machine_status
      - kwargs:
            machines:
              - kvm01
              - kvm02
            timeout: 1200 # in seconds
            req_status: "Ready"
      - require:
        - cmd: maas_login_admin
      ...

If module run w/\o any extra paremeters - `wait_for_machines_ready` will wait for defined in salt machines. In those case, will be usefull to skip some machines:

.. code-block:: bash

    > cat maas/machines/wait_for_machines_deployed.sls

    ...

    wait_for_machines_ready:
      module.run:
      - name: maas.wait_for_machine_status
      - kwargs:
            timeout: 1200 # in seconds
            req_status: "Deployed"
            ignore_machines:
               - kvm01 # in case it's broken or whatever
      - require:
        - cmd: maas_login_admin
      ...

List of available `req_status` defined in global variable:

.. code-block:: python

    STATUS_NAME_DICT = dict([
        (0, 'New'), (1, 'Commissioning'), (2, 'Failed commissioning'),
        (3, 'Missing'), (4, 'Ready'), (5, 'Reserved'), (10, 'Allocated'),
        (9, 'Deploying'), (6, 'Deployed'), (7, 'Retired'), (8, 'Broken'),
        (11, 'Failed deployment'), (12, 'Releasing'),
        (13, 'Releasing failed'), (14, 'Disk erasing'),
        (15, 'Failed disk erasing')])


Read more
=========

* https://maas.io/

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