#!/bin/bash
# Nivuus - Cloud Gaming Server Installation Script
# One-line install for complete system configuration

set -e

# NIVUUS_DIR resolves to the script's own directory unless overridden via env.
# The Nivuus installer (install-engine) sets NIVUUS_DIR=/opt/nivuus inside the chroot.
NIVUUS_DIR="${NIVUUS_DIR:-$(cd "$(dirname "$(readlink -f "$0")")" && pwd)}"
INSTALL_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"

# Non-interactive mode: skip all confirmation prompts (assume "yes").
# Triggered by `--non-interactive`/`-y` flag or NIVUUS_ASSUME_YES=1 env var.
NIVUUS_ASSUME_YES="${NIVUUS_ASSUME_YES:-0}"
for arg in "$@"; do
    case "$arg" in
        --non-interactive|-y|--yes) NIVUUS_ASSUME_YES=1 ;;
    esac
done

echo "========================================"
echo "Nivuus Installation"
echo "Cloud Gaming Server Configuration"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo ./install.sh)"
    exit 1
fi

# Detect CPU architecture
echo "Detecting hardware..."
CPU_MODEL=$(lscpu | grep "Model name" | cut -d':' -f2 | xargs)
echo "  CPU: $CPU_MODEL"

# Check for hybrid CPU (P+E cores)
if ! lscpu | grep -q "Model name.*12900K"; then
    echo "⚠️  Warning: This configuration is optimized for Intel i9-12900K"
    echo "   Your CPU: $CPU_MODEL"
    if [ "$NIVUUS_ASSUME_YES" = "1" ]; then
        echo "   (non-interactive: continuing anyway)"
    else
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
apt-get update -qq
apt-get install -y \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    bridge-utils \
    virt-manager \
    ovmf \
    stress-ng \
    lm-sensors \
    python3-pip

echo "✅ Dependencies installed"

# Setup CPU thermal optimization
echo ""
echo "Installing CPU thermal optimization..."
cp "$NIVUUS_DIR/scripts/optimize-cpu-thermal.sh" "$INSTALL_DIR/optimize-cpu-thermal.sh"
chmod +x "$INSTALL_DIR/optimize-cpu-thermal.sh"

# Create systemd service
cat > "$SYSTEMD_DIR/cpu-thermal-optimization.service" <<EOF
[Unit]
Description=CPU Thermal Optimization (P-cores 3600MHz + E-cores 2000MHz powersave)
After=multi-user.target

[Service]
Type=oneshot
ExecStart=$INSTALL_DIR/optimize-cpu-thermal.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cpu-thermal-optimization.service
echo "✅ CPU thermal optimization service installed"

# Configure hugepages
echo ""
echo "Configuring hugepages..."
HUGEPAGES_NEEDED=8192  # 16GB / 2MB

if ! grep -q "vm.nr_hugepages" /etc/sysctl.conf; then
    echo "vm.nr_hugepages = $HUGEPAGES_NEEDED" >> /etc/sysctl.conf
    sysctl -p
    echo "✅ Hugepages configured ($HUGEPAGES_NEEDED pages)"
else
    echo "ℹ️  Hugepages already configured"
fi

# Update GRUB for CPU isolation and IOMMU
echo ""
echo "Updating GRUB configuration..."
GRUB_FILE="/etc/default/grub"

# CPU isolation range and IOMMU type are parameterisable so the generic Nivuus
# installer can pass values computed from the actual hardware (see install-engine
# hardware detection). Defaults match the original i9-12900K configuration.
NIVUUS_ISOLCPUS="${NIVUUS_ISOLCPUS:-0-15}"
NIVUUS_IOMMU="${NIVUUS_IOMMU:-intel_iommu=on iommu=pt}"
# vfio-pci.ids=<vendor:device,...> for GPU passthrough (optional, auto-detected).
NIVUUS_VFIO_IDS="${NIVUUS_VFIO_IDS:-}"

NIVUUS_GRUB_PARAMS="isolcpus=${NIVUUS_ISOLCPUS} ${NIVUUS_IOMMU}"
if [ -n "$NIVUUS_VFIO_IDS" ]; then
    NIVUUS_GRUB_PARAMS="$NIVUUS_GRUB_PARAMS vfio-pci.ids=${NIVUUS_VFIO_IDS}"
fi

if ! grep -q "isolcpus=" "$GRUB_FILE"; then
    # Backup GRUB config
    cp "$GRUB_FILE" "${GRUB_FILE}.nivuus-backup"

    # Get current GRUB_CMDLINE_LINUX_DEFAULT
    CURRENT_CMDLINE=$(grep "^GRUB_CMDLINE_LINUX_DEFAULT" "$GRUB_FILE" | cut -d'"' -f2)

    # Add Nivuus parameters
    NEW_CMDLINE="$CURRENT_CMDLINE $NIVUUS_GRUB_PARAMS"

    # Update GRUB
    sed -i "s/^GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT=\"$NEW_CMDLINE\"/" "$GRUB_FILE"

    update-grub
    echo "✅ GRUB updated ($NIVUUS_GRUB_PARAMS) (requires reboot)"
    NEEDS_REBOOT=1
else
    echo "ℹ️  GRUB already configured"
fi

# Configure VFIO modules
echo ""
echo "Configuring VFIO modules..."
MODULES_FILE="/etc/modules"

for module in vfio vfio_iommu_type1 vfio_pci; do
    if ! grep -q "^$module$" "$MODULES_FILE"; then
        echo "$module" >> "$MODULES_FILE"
    fi
done

echo "✅ VFIO modules configured"

# Apply thermal optimization immediately (skipped inside a chroot/install image:
# CPU frequency controls under /sys are not writable from the installer chroot;
# the cpu-thermal-optimization.service will apply them on first real boot).
echo ""
if [ "${NIVUUS_IN_CHROOT:-0}" = "1" ]; then
    echo "Skipping immediate thermal optimization (chroot install) — will run on first boot."
else
    echo "Applying CPU thermal optimization..."
    "$INSTALL_DIR/optimize-cpu-thermal.sh" || \
        echo "⚠️  Could not apply thermal optimization now (will apply on next boot)"
fi

echo ""
echo "========================================"
echo "Installation Summary"
echo "========================================"
echo ""
echo "✅ Dependencies installed"
echo "✅ CPU thermal optimization configured"
echo "✅ Hugepages configured (8192 pages)"
echo "✅ GRUB updated (CPU isolation + IOMMU)"
echo "✅ VFIO modules configured"
echo ""

if [ -n "$NEEDS_REBOOT" ]; then
    echo "⚠️  REBOOT REQUIRED to apply kernel parameters"
    echo ""
    echo "After reboot, run:"
    echo "  sudo $NIVUUS_DIR/scripts/validate-install.sh"
else
    echo "ℹ️  No reboot required"
fi

echo ""
echo "Next steps:"
echo "  1. Configure GPU passthrough (edit GRUB vfio-pci.ids)"
echo "  2. Create Windows VM using template:"
echo "     virsh define $NIVUUS_DIR/configs/vm-template.xml"
echo "  3. Run validation:"
echo "     sudo $NIVUUS_DIR/scripts/validate-install.sh"
echo ""
echo "Documentation: $NIVUUS_DIR/docs/"
echo ""
echo "Nivuus installation complete!"
