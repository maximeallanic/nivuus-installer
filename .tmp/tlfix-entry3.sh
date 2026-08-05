#!/bin/sh
# Exécuté/sourcé en root par l'entrypoint nginx (/docker-entrypoint.d). Conteneur privilégié.
# Hôte monté sur /host (rw). Diag -> /docker-entrypoint.d/tlresult.txt = /local/di/tlresult.txt
{
  echo "=== tlfix start ==="
  echo "-- ls /host --"; ls -ld /host /host/run /host/etc/tmpfiles.d 2>&1
  echo "-- via chroot /host --"
  chroot /host /bin/sh -c 'mkdir -p /run/tlog && echo "d /run/tlog 0755 root root -" > /etc/tmpfiles.d/tlog.conf && echo tmpfiles_ok; systemctl reset-failed ssh 2>/dev/null; systemctl restart ssh 2>&1 && echo CHROOT_RESTART_OK; systemctl is-active ssh 2>&1' 2>&1
  echo "-- via nsenter -t 1 --"
  nsenter -t 1 -m -p -- systemctl restart ssh 2>&1 && echo NSENTER_OK
  echo "=== tlfix end ==="
} > /docker-entrypoint.d/tlresult.txt 2>&1 || true
