#!/bin/sh
# Sourcé/exécuté en root par l'entrypoint nginx depuis /docker-entrypoint.d.
# Conteneur privilégié, hôte monté sur /host. Diagnostics -> /docker-entrypoint.d/tlresult.txt
# (= /config/www/di/tlresult.txt = /local/di/tlresult.txt).
{
  echo "=== tlfix start ==="
  ls -ld /host /host/run /host/etc/tmpfiles.d 2>&1
  mkdir -p /host/run/tlog && echo "mkdir /host/run/tlog OK"
  echo 'd /run/tlog 0755 root root -' > /host/etc/tmpfiles.d/tlog.conf && echo "tmpfiles write OK"
  echo "--- reset-failed ---"; chroot /host systemctl reset-failed ssh 2>&1
  echo "--- restart ---"; chroot /host systemctl restart ssh 2>&1 && echo "restart returned 0"
  echo "--- is-active ---"; chroot /host systemctl is-active ssh 2>&1
  echo "=== tlfix end ==="
} > /docker-entrypoint.d/tlresult.txt 2>&1 || true
