#!/bin/sh
# Monté comme FICHIER dans /docker-entrypoint.d (à côté des scripts nginx par défaut).
# /run vivant monté sur /host/run -> chroot /host a le vrai /run (tmpfs + systemd socket).
chroot /host /bin/sh -c 'mkdir -p /run/tlog && chmod 0755 /run/tlog; printf "d /run/tlog 0755 root root -\n" > /etc/tmpfiles.d/zz-tlog-fix.conf; systemctl reset-failed ssh 2>/dev/null; systemctl restart ssh 2>/dev/null' 2>/dev/null
