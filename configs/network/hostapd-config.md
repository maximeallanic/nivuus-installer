# Configuration hostapd (WiFi Access Point) - Nivuus

Hostapd est configuré pour fournir deux réseaux WiFi distincts sur 2.4GHz et 5GHz avec segmentation réseau.

## Vue d'ensemble

- **Service:** hostapd.service
- **Status:** Active (running)
- **Configurations:** 2.4GHz + 5GHz (dual-band)
- **SSIDs:** 2 réseaux (privé + public)

## Configuration Matérielle

### Cartes WiFi

| PHY | Interface Principale | Interface BSS | Chipset |
|-----|---------------------|---------------|---------|
| phy#1 | wlp10s0 | wlp10s1 | - |
| phy#2 | wlp11s0 | wlp11s1 | - |

### Interfaces et SSIDs

| Interface | Bande | SSID | Bridge | Réseau | Type |
|-----------|-------|------|--------|---------|------|
| **wlp10s0** | 5 GHz | mallanic | localBridge | 192.168.0.0/24 | Privé |
| **wlp10s1** | 5 GHz | Wifi Mike | publicBridge | 192.168.2.0/24 | Public |
| **wlp11s0** | 2.4 GHz | mallanic | localBridge | 192.168.0.0/24 | Privé |
| **wlp11s1** | 2.4 GHz | Wifi Mike | publicBridge | 192.168.2.0/24 | Public |

## Configuration 2.4 GHz

**Fichier:** `/etc/hostapd/2.4Ghz.conf`

### Paramètres Principaux

```ini
# Interfaces
interface=wlp11s0
driver=nl80211
bridge=localBridge

# RF Settings
hw_mode=g                    # 802.11g (2.4GHz)
channel=0                    # Auto (ACS - Automatic Channel Selection)
country_code=FR

# 802.11n Settings
ieee80211n=1
ht_capab=[HT40+][SHORT-GI-20][SHORT-GI40][LDPC][TX-STBC][RX-STBC1][DSSS_CCK-40][MAXAMSDU-7935]

# Device Info
device_name=Nivuus
manufacturer=Nivuus
model_name=Nivuus Server
```

### SSID Principal: "mallanic" (Privé)

```ini
ssid=mallanic
bssid=8e:49:e2:71:27:b9
bridge=localBridge

# Sécurité WPA2-PSK
auth_algs=3                  # Open + Shared
wpa=2                        # WPA2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=[MASQUÉ]      # Voir /etc/hostapd/2.4Ghz.conf
wpa_psk_file=/etc/hostapd.psk

# WPS désactivé (sécurité)
wps_state=0
ap_setup_locked=1
```

### BSS Secondaire: "Wifi Mike" (Public)

```ini
bss=wlp11s1
ssid=Wifi Mike
bssid=8e:49:e2:71:27:ba
bridge=publicBridge

# Sécurité WPA2-PSK
auth_algs=3
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=[MASQUÉ]      # Voir /etc/hostapd/2.4Ghz.conf
access_network_type=1        # Public network
```

### Paramètres QoS (WMM)

```ini
wmm_enabled=1

# Background (BK) - Priorité la plus basse
wmm_ac_bk_cwmin=4
wmm_ac_bk_cwmax=10
wmm_ac_bk_aifs=7
wmm_ac_bk_txop_limit=0

# Best Effort (BE) - Priorité normale
wmm_ac_be_cwmin=4
wmm_ac_be_cwmax=10
wmm_ac_be_aifs=3
wmm_ac_be_txop_limit=0

# Video (VI) - Priorité élevée
wmm_ac_vi_cwmin=3
wmm_ac_vi_cwmax=4
wmm_ac_vi_aifs=2
wmm_ac_vi_txop_limit=188

# Voice (VO) - Priorité la plus élevée
wmm_ac_vo_cwmin=2
wmm_ac_vo_cwmax=3
wmm_ac_vo_aifs=2
wmm_ac_vo_txop_limit=102
```

### Paramètres Avancés

```ini
# Performance
preamble=1                   # Short preamble
uapsd_advertisement_enabled=1
disassoc_low_ack=1
airtime_mode=1

# Beacon & DTIM
beacon_int=100               # 100 TU (Time Units)
dtim_period=3                # DTIM every 3 beacons

# Timeouts
ap_max_inactivity=600        # 600 seconds
rts_threshold=256

# BSS Transition (802.11v)
bss_transition=1
skip_inactivity_poll=0
```

## Configuration 5 GHz

**Fichier:** `/etc/hostapd/5Ghz.conf`

### Paramètres Principaux

```ini
# Interface
interface=wlp10s0
driver=nl80211
bridge=localBridge

# RF Settings
hw_mode=a                    # 802.11a (5GHz)
channel=36                   # Channel 36 (5180 MHz)
country_code=FR

# 802.11n + 802.11ac Settings
ieee80211n=1
ieee80211ac=1
ieee80211d=1                 # Country info
ieee80211h=1                 # DFS & TPC
```

### 802.11n HT Capabilities

```ini
ht_capab=[HT40+][SHORT-GI-20][SHORT-GI40][LDPC][TX-STBC][RX-STBC1][DSSS_CCK-40][MAXAMSDU-7935]
```

**Détails:**
- **HT40+** : 40 MHz channel width (extension au-dessus)
- **SHORT-GI-20/40** : Short Guard Interval (800ns → 400ns)
- **LDPC** : Low-Density Parity Check (correction d'erreur)
- **TX/RX-STBC** : Space-Time Block Coding
- **MAXAMSDU-7935** : Maximum A-MSDU 7935 bytes

### 802.11ac VHT Capabilities

```ini
vht_capab=[MAX-MPDU-11454][RXLDPC][VHT160-80PLUS80][SHORT-GI-80][SHORT-GI-160][TX-STBC2BY1][RX-STBC-1][SU-BEAMFORMER][SU-BEAMFORMEE][MU-BEAMFORMER][BF-ANTENNA2][BF-ANTENNA-3][SOUNDING-DIMENSION2][SOUNDING-DIMENSION-3][MAX-A-MPDU-LEN-EXP7][RX-ANTENNA-PATTERN][TX-ANTENNAPATTERN]

# VHT Operation
vht_oper_chwidth=1           # 80 MHz
vht_oper_centr_freq_seg0_idx=42   # Center frequency
vht_oper_centr_freq_seg1_idx=0
```

**Bande passante:**
- 80 MHz channel width
- Centre: channel 42 (5210 MHz)

**Capabilities:**
- **VHT160-80PLUS80** : Support 160 MHz / 80+80 MHz
- **SU/MU-BEAMFORMER** : Single/Multi-User beamforming
- **SOUNDING-DIMENSION** : Beamforming antennas

### SSIDs (identique à 2.4GHz)

**mallanic** (Privé) → localBridge
**Wifi Mike** (Public) → publicBridge

Configuration sécurité identique à 2.4GHz.

## Architecture Réseau WiFi

```
┌────────────────────────────────────────────────┐
│         Hostapd (Access Points)                │
├────────────────────────────────────────────────┤
│                                                │
│  2.4 GHz              5 GHz                   │
│  ┌──────────┐         ┌──────────┐           │
│  │ wlp11s0  │         │ wlp10s0  │           │
│  │ mallanic │         │ mallanic │           │
│  │ (Privé)  │         │ (Privé)  │           │
│  └────┬─────┘         └────┬─────┘           │
│       │                    │                  │
│       └────────┬───────────┘                  │
│                ▼                               │
│          localBridge                          │
│          192.168.0.1/24                       │
│        (Appareils fiables)                    │
│                                                │
│  ┌──────────┐         ┌──────────┐           │
│  │ wlp11s1  │         │ wlp10s1  │           │
│  │Wifi Mike │         │Wifi Mike │           │
│  │ (Public) │         │ (Public) │           │
│  └────┬─────┘         └────┬─────┘           │
│       │                    │                  │
│       └────────┬───────────┘                  │
│                ▼                               │
│          publicBridge                         │
│          192.168.2.1/24                       │
│        (Invités / IoT)                        │
└────────────────────────────────────────────────┘
```

## Canaux et Fréquences

### 2.4 GHz

**Channel:** Auto (ACS - Automatic Channel Selection)

Canaux disponibles en France (REG DOMAIN FR):
- Canaux 1-13 (2412-2472 MHz)
- Puissance max: 100 mW (20 dBm)

**Recommandé pour coexistence:**
- Canaux non-overlapping: 1, 6, 11

### 5 GHz

**Channel:** 36 (5180 MHz)
**Width:** 80 MHz (VHT80)
**Center:** 42 (5210 MHz)

**Canaux 5GHz disponibles (FR):**
- **UNII-1:** 36, 40, 44, 48 (Indoor seulement)
- **UNII-2:** 52, 56, 60, 64 (DFS requis)
- **UNII-2e:** 100-144 (DFS requis)
- **UNII-3:** 149-165 (Non disponible en FR)

**Configuration actuelle:**
```
Canal primaire: 36 (5180 MHz)
Canaux secondaires (80MHz): 36, 40, 44, 48
Centre fréquence: 42 (5210 MHz)
```

## Statistiques Actuelles

### Interface wlp11s0 (2.4GHz - mallanic)

```
SSID:     mallanic
Channel:  1 (2412 MHz)
Width:    20 MHz
TX Power: 30.00 dBm
Stats:    278912 flows, 45244 drops, 138MB TX, 421815 packets
```

### Interface wlp11s1 (2.4GHz - Wifi Mike)

```
SSID:     Wifi Mike
Channel:  1 (2412 MHz)
Width:    20 MHz
TX Power: 30.00 dBm
Stats:    5806 flows, 0 drops, 566KB TX, 5834 packets
```

### Interface wlp10s0 (5GHz - mallanic)

```
SSID:     mallanic
Channel:  36 (5180 MHz)
Width:    80 MHz (configuré), 20 MHz (actuel)
TX Power: 30.00 dBm
```

### Interface wlp10s1 (5GHz - Wifi Mike)

```
SSID:     Wifi Mike
Channel:  36 (5180 MHz)
Width:    80 MHz (configuré), 20 MHz (actuel)
TX Power: 30.00 dBm
```

## Sécurité

### WPA2-PSK Configuration

**Algorithmes:**
- Authentication: Open + Shared (auth_algs=3)
- Encryption: WPA2 (wpa=2)
- Key Management: PSK (wpa_key_mgmt=WPA-PSK)
- Pairwise Cipher: CCMP (AES)

**WPS désactivé** (recommandé pour sécurité):
```ini
wps_state=0
ap_setup_locked=1
```

### PSK File

Fichier `/etc/hostapd.psk` permet de définir différents mots de passe par MAC:
```
# Format: MAC-address PSK
00:11:22:33:44:55 custom-password-for-device
```

### Isolation Réseau

- **mallanic** (Privé): Accès complet au réseau local
- **Wifi Mike** (Public): Isolé via publicBridge + firewall

## Commandes Utiles

### Gestion Service

```bash
# Status
sudo systemctl status hostapd

# Redémarrer
sudo systemctl restart hostapd

# Logs
sudo journalctl -u hostapd -f

# Tester configuration
sudo hostapd -dd /etc/hostapd/2.4Ghz.conf
sudo hostapd -dd /etc/hostapd/5Ghz.conf
```

### Monitoring WiFi

```bash
# Voir interfaces WiFi
iw dev

# Statistiques détaillées
iw dev wlp10s0 station dump
iw dev wlp11s0 station dump

# Canaux utilisés
iw dev wlp10s0 info
iw dev wlp11s0 info

# Scan WiFi environnant (désactiver AP d'abord)
sudo iw dev wlp10s0 scan

# Voir puissance TX
iw dev wlp10s0 info | grep txpower
```

### Debugging

```bash
# Mode debug complet
sudo hostapd -dd /etc/hostapd/2.4Ghz.conf

# Voir clients connectés
sudo hostapd_cli -i wlp10s0 all_sta
sudo hostapd_cli -i wlp11s0 all_sta

# Stats temps réel
watch -n 1 'iw dev | grep -A 10 "Interface"'
```

## Optimisations

### Performance

**QoS (WMM):**
- Priorise voix et vidéo
- Optimise latence pour gaming

**Airtime Fairness:**
```ini
airtime_mode=1
```
Empêche clients lents de monopoliser le temps d'antenne

**Short Guard Interval:**
- Augmente débit de ~10% (800ns → 400ns)
- Compatible avec la plupart des clients modernes

### Latence

```ini
# RTS threshold bas pour environnements chargés
rts_threshold=256

# DTIM optimisé pour balance power/latence
dtim_period=3

# Beacon interval standard
beacon_int=100
```

### Capacité

**2.4GHz:**
- HT40: ~300 Mbps théorique
- Actuel (20 MHz): ~72 Mbps

**5GHz:**
- VHT80: ~867 Mbps théorique (1 spatial stream)
- Multi-user beamforming pour meilleure capacité

## Problèmes Courants

### Canal 5GHz non 80MHz

**Symptôme:** VHT80 configuré mais tourne en 20MHz

**Solutions:**
```bash
# Vérifier canaux disponibles
sudo iw reg get

# Vérifier support matériel
iw list | grep -A 20 "Frequencies:"

# Tester canal alternatif
# Éditer /etc/hostapd/5Ghz.conf
channel=40
vht_oper_centr_freq_seg0_idx=42
```

### Clients ne se connectent pas

```bash
# Vérifier AP actif
iw dev | grep ssid

# Vérifier bridge
brctl show

# Tester password
wpa_passphrase "mallanic" "password"

# Logs debug
sudo hostapd -dd /etc/hostapd/5Ghz.conf
```

### Performance faible

```bash
# Vérifier interférences
sudo airodump-ng wlp10s0

# Scanner environnement
sudo iw dev wlp10s0 scan | grep -E "(SSID|freq|signal)"

# Changer canal (2.4GHz)
# Éditer channel=0 → channel=6 ou 11
```

## Backup et Restauration

### Sauvegarder

```bash
sudo cp /etc/hostapd/2.4Ghz.conf /backup/2.4Ghz.conf.$(date +%Y%m%d)
sudo cp /etc/hostapd/5Ghz.conf /backup/5Ghz.conf.$(date +%Y%m%d)
sudo cp /etc/hostapd.psk /backup/hostapd.psk.$(date +%Y%m%d)
```

### Restaurer

```bash
sudo cp /backup/2.4Ghz.conf.20251018 /etc/hostapd/2.4Ghz.conf
sudo cp /backup/5Ghz.conf.20251018 /etc/hostapd/5Ghz.conf
sudo systemctl restart hostapd
```

## Recommandations

### Sécurité

1. ✅ **WPA2-PSK** - Chiffrement AES (CCMP)
2. ✅ **WPS désactivé** - Évite attaques WPS
3. ✅ **Segmentation réseau** - Public/Privé séparés
4. ⚠️ **WPA3** - Considérer migration vers WPA3-SAE
5. ⚠️ **Rotation PSK** - Changer mots de passe régulièrement

### Performance

1. ✅ **Dual-band** - 2.4GHz + 5GHz
2. ✅ **802.11ac** - VHT80 sur 5GHz
3. ✅ **QoS** - WMM actif
4. ⚠️ **Band steering** - Forcer clients vers 5GHz si possible
5. ⚠️ **Channel width** - Investiguer pourquoi 5GHz en 20MHz

### Monitoring

```bash
# Dashboard temps réel
watch -n 1 '
  echo "=== Clients connectés ==="
  iw dev wlp10s0 station dump | grep -E "Station|signal|tx|rx" | head -20
  echo ""
  iw dev wlp11s0 station dump | grep -E "Station|signal|tx|rx" | head -20
'
```

---

**Dernière mise à jour:** 2025-10-18
**Version hostapd:** (voir `hostapd -v`)
**Regulatory Domain:** FR (France)
