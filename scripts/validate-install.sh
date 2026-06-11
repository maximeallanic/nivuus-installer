#!/bin/bash
# Nivuus Installation Validation Script
# Verifies that all components are correctly configured

echo "========================================"
echo "Nivuus Installation Validation"
echo "========================================"
echo ""

PASS=0
WARN=0
FAIL=0

# Helper functions
check_pass() {
    echo "  ✅ $1"
    ((PASS++))
}

check_warn() {
    echo "  ⚠️  $1"
    ((WARN++))
}

check_fail() {
    echo "  ❌ $1"
    ((FAIL++))
}

# Check 1: CPU Isolation
echo "1. CPU Isolation (isolcpus=0-15)"
if cat /proc/cmdline | grep -q "isolcpus=0-15"; then
    check_pass "Kernel parameter configured"

    # Verify isolated CPUs
    if [ -f /sys/devices/system/cpu/isolated ]; then
        ISOLATED=$(cat /sys/devices/system/cpu/isolated)
        if [ "$ISOLATED" = "0-15" ]; then
            check_pass "CPUs 0-15 are isolated"
        else
            check_warn "Isolated CPUs: $ISOLATED (expected 0-15)"
        fi
    else
        check_warn "Cannot verify isolated CPUs (file not found)"
    fi
else
    check_fail "isolcpus not configured in kernel parameters"
fi

# Check 2: IOMMU
echo ""
echo "2. IOMMU Configuration"
if cat /proc/cmdline | grep -q "intel_iommu=on"; then
    check_pass "IOMMU enabled in kernel"

    if dmesg | grep -q "IOMMU enabled"; then
        check_pass "IOMMU active"
    else
        check_warn "IOMMU may not be active (check dmesg)"
    fi
else
    check_fail "IOMMU not enabled in kernel parameters"
fi

# Check 3: VFIO Modules
echo ""
echo "3. VFIO Modules"
for module in vfio vfio_iommu_type1 vfio_pci; do
    if lsmod | grep -q "^$module"; then
        check_pass "$module loaded"
    else
        check_warn "$module not loaded"
    fi
done

# Check 4: Hugepages
echo ""
echo "4. Hugepages Configuration"
HUGEPAGES_TOTAL=$(cat /proc/meminfo | grep HugePages_Total | awk '{print $2}')
HUGEPAGES_FREE=$(cat /proc/meminfo | grep HugePages_Free | awk '{print $2}')

if [ "$HUGEPAGES_TOTAL" -eq 8192 ]; then
    check_pass "Hugepages configured (8192 pages)"
    check_pass "  Free: $HUGEPAGES_FREE / $HUGEPAGES_TOTAL"
elif [ "$HUGEPAGES_TOTAL" -gt 0 ]; then
    check_warn "Hugepages: $HUGEPAGES_TOTAL (expected 8192)"
else
    check_fail "Hugepages not configured"
fi

# Check 5: CPU Thermal Optimization
echo ""
echo "5. CPU Thermal Optimization"

# Check service
if systemctl is-enabled cpu-thermal-optimization.service &>/dev/null; then
    check_pass "Service enabled"
else
    check_fail "Service not enabled"
fi

if systemctl is-active cpu-thermal-optimization.service &>/dev/null; then
    check_pass "Service active"
else
    check_warn "Service not running"
fi

# Check P-cores configuration
PCORE_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq 2>/dev/null || echo "0")
PCORE_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "unknown")

if [ "$PCORE_FREQ" -eq 3600000 ]; then
    check_pass "P-cores max frequency: 3600 MHz"
else
    check_warn "P-cores max frequency: $((PCORE_FREQ/1000)) MHz (expected 3600)"
fi

if [ "$PCORE_GOV" = "performance" ]; then
    check_pass "P-cores governor: performance"
else
    check_warn "P-cores governor: $PCORE_GOV (expected performance)"
fi

# Check E-cores configuration
if [ -d "/sys/devices/system/cpu/cpu16" ]; then
    ECORE_FREQ=$(cat /sys/devices/system/cpu/cpu16/cpufreq/scaling_max_freq 2>/dev/null || echo "0")
    ECORE_GOV=$(cat /sys/devices/system/cpu/cpu16/cpufreq/scaling_governor 2>/dev/null || echo "unknown")

    if [ "$ECORE_FREQ" -eq 2000000 ]; then
        check_pass "E-cores max frequency: 2000 MHz"
    else
        check_warn "E-cores max frequency: $((ECORE_FREQ/1000)) MHz (expected 2000)"
    fi

    if [ "$ECORE_GOV" = "powersave" ]; then
        check_pass "E-cores governor: powersave"
    else
        check_warn "E-cores governor: $ECORE_GOV (expected powersave)"
    fi
else
    check_warn "E-cores not detected (CPU may not be hybrid)"
fi

# Check 6: libvirt
echo ""
echo "6. Virtualization"
if systemctl is-active libvirtd &>/dev/null; then
    check_pass "libvirtd running"
else
    check_fail "libvirtd not running"
fi

# Check if VM exists
if virsh list --all 2>/dev/null | grep -q "Windows"; then
    check_pass "Windows VM configured"

    # Check VM CPU pinning
    if virsh vcpupin Windows 2>/dev/null | grep -q "0.*0"; then
        check_pass "VM CPU pinning configured"
    else
        check_warn "VM CPU pinning may not be configured"
    fi
else
    check_warn "Windows VM not found (expected for fresh install)"
fi

# Check 7: Sensors
echo ""
echo "7. Temperature Monitoring"
if command -v sensors &>/dev/null; then
    check_pass "lm-sensors installed"

    PKG_TEMP=$(sensors coretemp-isa-0000 2>/dev/null | grep "Package id" | grep -oP '\+\K[0-9]+' | head -1)
    if [ -n "$PKG_TEMP" ]; then
        check_pass "Current CPU Package temp: ${PKG_TEMP}°C"

        if [ "$PKG_TEMP" -lt 60 ]; then
            check_pass "  Temperature: Good (idle)"
        elif [ "$PKG_TEMP" -lt 80 ]; then
            check_warn "  Temperature: Warm ($PKG_TEMP°C)"
        else
            check_fail "  Temperature: Too hot! ($PKG_TEMP°C)"
        fi
    else
        check_warn "Cannot read CPU temperature"
    fi
else
    check_fail "lm-sensors not installed"
fi

# Summary
echo ""
echo "========================================"
echo "Validation Summary"
echo "========================================"
echo ""
echo "  ✅ Passed:  $PASS"
echo "  ⚠️  Warnings: $WARN"
echo "  ❌ Failed:  $FAIL"
echo ""

if [ $FAIL -eq 0 ] && [ $WARN -eq 0 ]; then
    echo "🎉 Perfect! All checks passed."
    echo ""
    echo "Next steps:"
    echo "  1. Create Windows VM (if not done)"
    echo "  2. Configure GPU passthrough"
    echo "  3. Run thermal stress test:"
    echo "     sudo /home/mallanic/Projects/Nivuus/tests/stress-test.sh"
    exit 0
elif [ $FAIL -eq 0 ]; then
    echo "✅ Installation OK (some warnings)"
    echo ""
    echo "Review warnings above and fix if needed."
    exit 0
else
    echo "❌ Installation incomplete"
    echo ""
    echo "Please fix the failed checks above."
    echo "Documentation: /home/mallanic/Projects/Nivuus/docs/"
    exit 1
fi
