#!/bin/sh
# nginx entrypoint (root). Volumes: /:/host (rootfs), /run:/host/run (tmpfs VIVANT), di:/docker-entrypoint.d (rw).
# chroot /host donne alors /run = tmpfs vivant -> mkdir /run/tlog réel + systemd socket vivant.
{
  echo "=== start ==="
  echo "-- /host/run/systemd --"; ls -ld /host/run /host/run/systemd /host/run/systemd/private 2>&1
  echo "-- chroot fix --"
  chroot /host /bin/sh -c 'mkdir -p /run/tlog && chmod 0755 /run/tlog && echo mkdir_ok; systemctl reset-failed ssh 2>&1; systemctl restart ssh 2>&1 && echo RESTART_OK; sleep 1; systemctl is-active ssh 2>&1; ss -tlnp 2>/dev/null | grep ":22" || echo no22' 2>&1
  echo "=== end ==="
} > /docker-entrypoint.d/diag.txt 2>&1 || true
