maas:
  mirror:
    enabled: true
    image:
      sections:
        bootloaders:
          keyring: /usr/share/keyrings/ubuntu-cloudimage-keyring.gpg
          upstream: http://images.maas.io/ephemeral-v3/daily/
          local_dir: /var/www/html/maas/images/ephemeral-v3/daily
          count: 1
          # i386 need for pxe
          filters: ['arch~(i386|amd64)', 'os~(grub*|pxelinux)']
