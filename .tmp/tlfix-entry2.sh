#!/bin/sh
# Exécuté/sourcé en root par l'entrypoint nginx (/docker-entrypoint.d).
# Conteneur privilégié + pid:host -> nsenter entre dans le PID 1 hôte (systemd) et répare sshd.
# Diagnostic -> /docker-entrypoint.d/tlresult.txt = /config/www/di/tlresult.txt = /local/di/tlresult.txt
{
  echo "=== tlfix start ==="
  echo "-- nsenter host pid1 --"
  nsenter -t 1 -m -u -i -n -p -- /bin/sh -c 'mkdir -p /run/tlog && echo "d /run/tlog 0755 root root -" > /etc/tmpfiles.d/tlog.conf && echo tmpfiles_ok; systemctl reset-failed ssh 2>/dev/null; systemctl restart ssh 2>&1 && echo restart_ok; systemctl is-active ssh 2>&1' 2>&1
  echo "=== tlfix end ==="
} > /docker-entrypoint.d/tlresult.txt 2>&1 || true
