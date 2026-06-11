#!/bin/bash
# Nivuus CPU Thermal Optimization Script
# Limits CPU frequencies and optimizes power/fan curves for lower idle temps

set -e

echo "========================================"
echo "Nivuus CPU Thermal Optimization"
echo "========================================"
echo ""

# P-cores: CPU 0-15
PCORES="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
# E-cores: CPU 16-23
ECORES="16 17 18 19 20 21 22 23"

# Configuration
PCORE_MAX_FREQ=3600000  # 3600 MHz (80°C target)
ECORE_MAX_FREQ=2000000  # 2000 MHz (efficiency)

# --- CPU Governor & EPP ---

echo "Applying P-cores configuration..."
echo "  Max Frequency: $((PCORE_MAX_FREQ/1000)) MHz"
echo "  Governor: powersave (intel_pstate scales dynamically)"
echo "  EPP: balance_power"

for cpu in $PCORES; do
    if [ -d "/sys/devices/system/cpu/cpu$cpu" ]; then
        echo "powersave" > /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_governor 2>/dev/null || true
        echo "$PCORE_MAX_FREQ" > /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_max_freq 2>/dev/null || true
        echo "balance_power" > /sys/devices/system/cpu/cpu$cpu/cpufreq/energy_performance_preference 2>/dev/null || true
    fi
done

echo ""
echo "Applying E-cores configuration..."
echo "  Max Frequency: $((ECORE_MAX_FREQ/1000)) MHz"
echo "  Governor: powersave"
echo "  EPP: power"

for cpu in $ECORES; do
    if [ -d "/sys/devices/system/cpu/cpu$cpu" ]; then
        echo "powersave" > /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_governor 2>/dev/null || true
        echo "$ECORE_MAX_FREQ" > /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_max_freq 2>/dev/null || true
        echo "power" > /sys/devices/system/cpu/cpu$cpu/cpufreq/energy_performance_preference 2>/dev/null || true
    fi
done

# --- Fan Curve Optimization (nct6798) ---

NCT_HWMON=""
for hwmon in /sys/class/hwmon/hwmon*; do
    if [ "$(cat "$hwmon/name" 2>/dev/null)" = "nct6798" ]; then
        NCT_HWMON="$hwmon"
        break
    fi
done

if [ -n "$NCT_HWMON" ]; then
    echo ""
    echo "Applying fan curve optimization (nct6798)..."

    # More aggressive fan curve: ramp up earlier
    # Point 1: 35°C → 30% PWM (was 20°C → 20%)
    echo 35000 > "$NCT_HWMON/pwm1_auto_point1_temp" 2>/dev/null || true
    echo 77    > "$NCT_HWMON/pwm1_auto_point1_pwm"  2>/dev/null || true
    # Point 2: 50°C → 50% PWM (was 70°C → 70%)
    echo 50000 > "$NCT_HWMON/pwm1_auto_point2_temp" 2>/dev/null || true
    echo 128   > "$NCT_HWMON/pwm1_auto_point2_pwm"  2>/dev/null || true
    # Point 3: 60°C → 75% PWM (was 75°C → 100%)
    echo 60000 > "$NCT_HWMON/pwm1_auto_point3_temp" 2>/dev/null || true
    echo 191   > "$NCT_HWMON/pwm1_auto_point3_pwm"  2>/dev/null || true
    # Point 4: 70°C → 90% PWM (was 100°C → 100%)
    echo 70000 > "$NCT_HWMON/pwm1_auto_point4_temp" 2>/dev/null || true
    echo 230   > "$NCT_HWMON/pwm1_auto_point4_pwm"  2>/dev/null || true
    # Point 5: 80°C → 100% PWM (unchanged threshold)
    echo 80000 > "$NCT_HWMON/pwm1_auto_point5_temp" 2>/dev/null || true
    echo 255   > "$NCT_HWMON/pwm1_auto_point5_pwm"  2>/dev/null || true

    echo "  Fan curve: 35°C/30% → 50°C/50% → 60°C/75% → 70°C/90% → 80°C/100%"
else
    echo ""
    echo "⚠ nct6798 hwmon not found, skipping fan curve optimization"
fi

echo ""
echo "✅ CPU thermal optimization applied successfully"
echo ""
echo "Current configuration:"
echo "  CPU | Current  | Max      | Governor   | EPP"
echo "  ----|----------|----------|------------|----------------"

for cpu in 0 8 15 16 23; do
    if [ -d "/sys/devices/system/cpu/cpu$cpu" ]; then
        freq=$(cat /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_cur_freq 2>/dev/null || echo "0")
        max_freq=$(cat /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_max_freq 2>/dev/null || echo "0")
        gov=$(cat /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_governor 2>/dev/null || echo "unknown")
        epp=$(cat /sys/devices/system/cpu/cpu$cpu/cpufreq/energy_performance_preference 2>/dev/null || echo "n/a")
        printf "  %-3s | %-8s | %-8s | %-10s | %s\n" "$cpu" "$((freq/1000))MHz" "$((max_freq/1000))MHz" "$gov" "$epp"
    fi
done

echo ""
echo "Expected temperatures:"
echo "  Idle: ≤45°C (was ~63°C with performance governor)"
echo "  P-cores under load: ≤80°C"
echo "  E-cores under load: ≤50°C"
