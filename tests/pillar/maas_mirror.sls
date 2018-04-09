maas:
  mirror:
    enabled: true
    image:
      release:
        xenial:
          keyring: '/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg'
          upstream: 'http://images.maas.io/ephemeral-v3/daily/'
          local_dir: '/var/www/html/maas/images/ephemeral-v3/daily'
          arch: amd64
          subarch: 'generic|hwe-t'
          count: '1'
