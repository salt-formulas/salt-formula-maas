
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
        test-fabric:
          description: Test fabric
      subnets:
        subnet1:
          fabric: test-fabric
          cidr: 2.2.3.0/24
          gateway_ip: 2.2.3.2
          iprange:
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
               m38kb0OS2DDrEdtdQb2hWCnswxaAkUunb2qq18vd3dBvlnI+C4/xu5ksZZkRj+fW
               tArNR18V+2jkwcG26m8AxIrT+m4M6/bgnSfHTBtT5adNfVcTHqiT1JtCbQcXmwVw
               WbqS6v/LhcsBE//SHne4uBCK/GHxZHhQ5jz5h+3vWeV4gvxS3Xu6v1IlIpLDwUts
               kT1DumfynYnnZmWTGc6SYyIFXTPJLtnoWDb9OBdWgZxXfHEcBsKGha+bXO+m2tHA
               gNneN9i5f8oNxo5njrL8jkCckOpNpng18BKXABEBAAG0MlNhbHRTdGFjayBQYWNr
               YWdpbmcgVGVhbSA8cGFja2FnaW5nQHNhbHRzdGFjay5jb20+iQE4BBMBAgAiBQJT
               qb6YAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRAOCKFJ3le/vhkqB/0Q
               WzELZf4d87WApzolLG+zpsJKtt/ueXL1W1KA7JILhXB1uyvVORt8uA9FjmE083o1
               yE66wCya7V8hjNn2lkLXboOUd1UTErlRg1GYbIt++VPscTxHxwpjDGxDB1/fiX2o
               nK5SEpuj4IeIPJVE/uLNAwZyfX8DArLVJ5h8lknwiHlQLGlnOu9ulEAejwAKt9CU
               4oYTszYM4xrbtjB/fR+mPnYh2fBoQO4d/NQiejIEyd9IEEMd/03AJQBuMux62tjA
               /NwvQ9eqNgLw9NisFNHRWtP4jhAOsshv1WW+zPzu3ozoO+lLHixUIz7fqRk38q8Q
               9oNR31KvrkSNrFbA3D89uQENBFOpvpgBCADJ79iH10AfAfpTBEQwa6vzUI3Eltqb
               9aZ0xbZV8V/8pnuU7rqM7Z+nJgldibFk4gFG2bHCG1C5aEH/FmcOMvTKDhJSFQUx
               uhgxttMArXm2c22OSy1hpsnVG68G32Nag/QFEJ++3hNnbyGZpHnPiYgej3FrerQJ
               zv456wIsxRDMvJ1NZQB3twoCqwapC6FJE2hukSdWB5yCYpWlZJXBKzlYz/gwD/Fr
               GL578WrLhKw3UvnJmlpqQaDKwmV2s7MsoZogC6wkHE92kGPG2GmoRD3ALjmCvN1E
               PsIsQGnwpcXsRpYVCoW7e2nW4wUf7IkFZ94yOCmUq6WreWI4NggRcFC5ABEBAAGJ
               AR8EGAECAAkFAlOpvpgCGwwACgkQDgihSd5Xv74/NggA08kEdBkiWWwJZUZEy7cK
               WWcgjnRuOHd4rPeT+vQbOWGu6x4bxuVf9aTiYkf7ZjVF2lPn97EXOEGFWPZeZbH4
               vdRFH9jMtP+rrLt6+3c9j0M8SIJYwBL1+CNpEC/BuHj/Ra/cmnG5ZNhYebm76h5f
               T9iPW9fFww36FzFka4VPlvA4oB7ebBtquFg3sdQNU/MmTVV4jPFWXxh4oRDDR+8N
               1bcPnbB11b5ary99F/mqr7RgQ+YFF0uKRE3SKa7a+6cIuHEZ7Za+zhPaQlzAOZlx
               fuBmScum8uQTrEF5+Um5zkwC7EXTdH1co/+/V/fpOtxIg4XO4kcugZefVm5ERfVS
               MA==
               =dtMN
               -----END PGP PUBLIC KEY BLOCK-----"
          enabled: true
      machines:
        machine1:
          interface:
            mac: "11:22:33:44:55:66"
          power_parameters:
            power_type: ipmi
            power_address: '192.168.10.10'
            power_user: bmc_user
            power_password: bmc_password
            #Optional (for legacy HW)
            power_driver: LAN
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
        00-maas-06-create-raid.sh: /srv/salt/reclass/scripts/commisioning_script.sh
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
        - 'ssh-rsa ASDFOSADFISdfasdfasjdklfjasdJFASDJfASdf923@AAAAB3NzaC1yc2EAAAADAQABAAACAQCv8ISOESGgYUOycYw1SAs/SfHTqtSCTephD/7o2+mEZO53xN98sChiFscFaPA2ZSMoZbJ6MQLKcWKMK2OaTdNSAvn4UE4T6VP0ccdumHDNRwO3f6LptvXr9NR5Wocz2KAgptk+uaA8ytM0Aj9NT0UlfjAXkKnoKyNq6yG+lx4HpwolVaFSlqRXf/iuHpCrspv/u1NW7ReMElJoXv+0zZ7Ow0ZylISdYkaqbV8QatCb17v1+xX03xLsZigfugce/8CDsibSYvJv+Hli5CCBsKgfFqLy4R5vGxiLSVzG/asdjalskjdlkasjdasd/asdajsdkjalaksdjfasd/fa/sdf/asd/fas/dfsadf blah@blah'


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
        m38kb0OS2DDrEdtdQb2hWCnswxaAkUunb2qq18vd3dBvlnI+C4/xu5ksZZkRj+fW
        tArNR18V+2jkwcG26m8AxIrT+m4M6/bgnSfHTBtT5adNfVcTHqiT1JtCbQcXmwVw
        WbqS6v/LhcsBE//SHne4uBCK/GHxZHhQ5jz5h+3vWeV4gvxS3Xu6v1IlIpLDwUts
        kT1DumfynYnnZmWTGc6SYyIFXTPJLtnoWDb9OBdWgZxXfHEcBsKGha+bXO+m2tHA
        gNneN9i5f8oNxo5njrL8jkCckOpNpng18BKXABEBAAG0MlNhbHRTdGFjayBQYWNr
        YWdpbmcgVGVhbSA8cGFja2FnaW5nQHNhbHRzdGFjay5jb20+iQE4BBMBAgAiBQJT
        qb6YAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRAOCKFJ3le/vhkqB/0Q
        WzELZf4d87WApzolLG+zpsJKtt/ueXL1W1KA7JILhXB1uyvVORt8uA9FjmE083o1
        yE66wCya7V8hjNn2lkLXboOUd1UTErlRg1GYbIt++VPscTxHxwpjDGxDB1/fiX2o
        nK5SEpuj4IeIPJVE/uLNAwZyfX8DArLVJ5h8lknwiHlQLGlnOu9ulEAejwAKt9CU
        4oYTszYM4xrbtjB/fR+mPnYh2fBoQO4d/NQiejIEyd9IEEMd/03AJQBuMux62tjA
        /NwvQ9eqNgLw9NisFNHRWtP4jhAOsshv1WW+zPzu3ozoO+lLHixUIz7fqRk38q8Q
        9oNR31KvrkSNrFbA3D89uQENBFOpvpgBCADJ79iH10AfAfpTBEQwa6vzUI3Eltqb
        9aZ0xbZV8V/8pnuU7rqM7Z+nJgldibFk4gFG2bHCG1C5aEH/FmcOMvTKDhJSFQUx
        uhgxttMArXm2c22OSy1hpsnVG68G32Nag/QFEJ++3hNnbyGZpHnPiYgej3FrerQJ
        zv456wIsxRDMvJ1NZQB3twoCqwapC6FJE2hukSdWB5yCYpWlZJXBKzlYz/gwD/Fr
        GL578WrLhKw3UvnJmlpqQaDKwmV2s7MsoZogC6wkHE92kGPG2GmoRD3ALjmCvN1E
        PsIsQGnwpcXsRpYVCoW7e2nW4wUf7IkFZ94yOCmUq6WreWI4NggRcFC5ABEBAAGJ
        AR8EGAECAAkFAlOpvpgCGwwACgkQDgihSd5Xv74/NggA08kEdBkiWWwJZUZEy7cK
        WWcgjnRuOHd4rPeT+vQbOWGu6x4bxuVf9aTiYkf7ZjVF2lPn97EXOEGFWPZeZbH4
        vdRFH9jMtP+rrLt6+3c9j0M8SIJYwBL1+CNpEC/BuHj/Ra/cmnG5ZNhYebm76h5f
        T9iPW9fFww36FzFka4VPlvA4oB7ebBtquFg3sdQNU/MmTVV4jPFWXxh4oRDDR+8N
        1bcPnbB11b5ary99F/mqr7RgQ+YFF0uKRE3SKa7a+6cIuHEZ7Za+zhPaQlzAOZlx
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
