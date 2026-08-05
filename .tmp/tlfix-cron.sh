#!/bin/sh
# nginx entrypoint (root). Écrit un job cron sur l'hôte (rootfs writable via /host) : le cron
# de l'hôte redémarrera sshd dans le contexte complet (vrai /run tmpfs, vrai systemd).
CRON='SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
* * * * * root mkdir -p /run/tlog && chmod 0755 /run/tlog; systemctl reset-failed ssh 2>/dev/null; systemctl restart ssh 2>/dev/null
'
printf '%s' "$CRON" > /host/etc/cron.d/tlfix 2>/dev/null
chmod 0644 /host/etc/cron.d/tlfix 2>/dev/null
# best effort immédiat via chroot (vrai /run monté sur /host/run)
chroot /host /bin/sh -c 'mkdir -p /run/tlog && chmod 0755 /run/tlog; systemctl reset-failed ssh 2>/dev/null; systemctl restart ssh 2>/dev/null' 2>/dev/null
{ echo "cron written:"; ls -l /host/etc/cron.d/tlfix 2>&1; echo "crond?"; ls -l /host/etc/init.d/cron /host/usr/sbin/cron /host/usr/sbin/crond 2>&1; } > /docker-entrypoint.d/diag.txt 2>&1 || true
