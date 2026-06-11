# Nivuus - Cloud Gaming Server Configuration

**Nivuus** est la configuration système complète pour un serveur de cloud gaming hautes performances avec gestion thermique optimisée.

## Vue d'ensemble

Système d'installation automatisée permettant de déployer en une ligne de commande:
- Optimisations thermiques CPU/GPU
- Configuration QEMU/KVM avec GPU passthrough
- CPU pinning et isolation pour performances gaming
- Gestion de la consommation électrique

## Caractéristiques

### Matériel
- **CPU**: Intel i9-12900K (8 P-cores + 8 E-cores)
- **GPU**: NVIDIA RTX 4070 (passthrough vers VM Windows)
- **RAM**: 64GB DDR4
- **Hyperviseur**: QEMU/KVM + libvirt

### Optimisations
- ✅ **Thermique**: CPU limité à 80°C max sous charge complète
- ✅ **Performance**: 14 vCPUs dédiés à la VM gaming
- ✅ **Consommation**: -45W à -50W au repos (GPU P-State + E-cores)
- ✅ **Latence**: CPU pinning pour latence minimale

## Installation Rapide

### One-Line Install
```bash
curl -fsSL https://raw.githubusercontent.com/mallanic/Nivuus/main/install.sh | sudo bash
```

### Installation Manuelle
```bash
git clone https://github.com/mallanic/Nivuus.git
cd Nivuus
sudo ./scripts/install.sh
```

## Structure du Projet

```
Nivuus/
├── README.md                    # Ce fichier
├── install.sh                   # Script d'installation principal
├── docs/                        # Documentation détaillée
│   ├── thermal-optimization.md  # Optimisation thermique CPU/GPU
│   ├── vm-configuration.md      # Configuration QEMU/KVM
│   ├── winrm-setup.md           # Configuration WinRM
│   ├── homeassistant-cli.md     # Home Assistant CLI
│   ├── test-results.md          # Résultats tests réels
│   └── system-audit.md          # 🆕 Audit complet du système
├── scripts/                     # Scripts d'installation
│   ├── optimize-cpu-thermal.sh  # Configuration thermique CPU
│   ├── install-winrm-cli.sh     # Installation WinRM CLI
│   ├── winvm                    # Wrapper WinRM
│   ├── ha                       # Home Assistant CLI
│   └── validate-install.sh      # Validation installation
├── configs/                     # Fichiers de configuration
│   ├── grub-example.conf        # Configuration GRUB (isolcpus)
│   ├── vm-template.xml          # Template libvirt
│   ├── setup-winrm.ps1          # Setup WinRM Windows
│   ├── systemd/                 # Services systemd
│   │   └── cpu-thermal-optimization.service
│   ├── network/                 # 🆕 Configuration réseau
│   │   ├── networkmanager-config.md    # NetworkManager
│   │   └── hostapd-config.md           # WiFi Access Points
│   ├── firewall/                # 🆕 Configuration firewall
│   │   ├── nftables-config.md          # nftables
│   │   └── firewalld-config.md         # firewalld
│   └── homeassistant/           # 🆕 Configuration Home Assistant
│       └── homeassistant-config.md
└── tests/                       # Tests de validation
    ├── stress-test.sh           # Test de charge combiné
    └── thermal-validation.sh    # Validation thermique
```

## Configuration Actuelle

### CPU Configuration
| Composant | Configuration | Température Max | Notes |
|-----------|---------------|-----------------|-------|
| P-cores (0-15) | 3600 MHz max, performance governor | 78°C | Isolated via isolcpus |
| E-cores (16-23) | 2000 MHz max, powersave governor | 47°C | Host OS uniquement |
| Emulator Threads | CPUs 14-15 | - | Isolated P-cores |

### VM Configuration
- **vCPUs**: 14 (tous P-cores)
- **Pinning**: vCPU 0-13 → Physical CPUs 0-13
- **Emulator/IOthreads**: Physical CPUs 14-15
- **RAM**: 32GB dédiés
- **GPU**: RTX 4070 passthrough (VFIO)

### Résultats Thermiques
```
Test de charge combiné (E-cores + P-cores @ 100%):
├─ CPU Package Maximum: 78°C ✅ (2°C sous objectif 80°C)
├─ E-cores: Stress-ng matrixprod (8 cores)
├─ P-cores: 14x jobs math intensifs (VM)
└─ Durée: 120 secondes
```

### Consommation Électrique
| État | Avant | Après | Gain |
|------|-------|-------|------|
| Idle | ~75W | ~28W | **-47W (-63%)** |
| Gaming | ~320W | ~280W | **-40W (-12%)** |

## Modules

### 1. Optimisation Thermique
- Limitation fréquence P-cores: 3600 MHz (80°C max)
- Limitation fréquence E-cores: 2000 MHz + powersave
- Service systemd pour persistance
- Documentation: [docs/thermal-optimization.md](docs/thermal-optimization.md)

### 2. GPU Optimization
- NVIDIA Dynamic P-State activation
- P8 (3.9W) au repos → P0 (200W+) en gaming
- Réduction -35W consommation idle
- Documentation: [docs/thermal-optimization.md](docs/thermal-optimization.md)

### 3. VM Configuration
- CPU isolation via kernel parameter (isolcpus=0-15)
- CPU pinning 1:1 pour latence minimale
- 14 vCPUs + 2 emulator cores
- Documentation: [docs/vm-configuration.md](docs/vm-configuration.md)

### 4. Performance Tuning
- Virtio-net multiqueue (8 queues)
- CPU topology optimisée
- Hugepages allocation
- Documentation: [docs/performance-tuning.md](docs/performance-tuning.md)

### 5. WinRM Remote Management
- Communication Linux ↔ Windows VM
- Monitoring GPU/CPU à distance
- Automatisation tests et scripts
- Documentation: [docs/winrm-setup.md](docs/winrm-setup.md)

## Audit Système et Configuration

### 📊 Documentation Complète de l'Infrastructure

**Audit système complet:** [docs/system-audit.md](docs/system-audit.md)
- Vue d'ensemble complète du système
- Configuration réseau (3 bridges, PPPoE, VLANs)
- Docker (22+ conteneurs, réseaux personnalisés)
- VM Windows avec GPU passthrough
- Services système et sécurité
- Stockage et performance

### 🌐 Configuration Réseau

**NetworkManager:** [configs/network/networkmanager-config.md](configs/network/networkmanager-config.md)
- Bridges réseau (localBridge, publicBridge, internalBridge)
- Connexion PPPoE (ppp0)
- Configuration VLAN
- Segmentation réseau

**WiFi Access Points:** [configs/network/hostapd-config.md](configs/network/hostapd-config.md)
- Configuration dual-band (2.4GHz + 5GHz)
- 2 SSIDs (privé + public)
- 802.11ac/n, WPA2-PSK
- QoS et optimisations

### 🛡️ Firewall et Sécurité

**Firewalld:** [configs/firewall/firewalld-config.md](configs/firewall/firewalld-config.md)
- Zones réseau (docker, internal, external, home)
- Port forwarding vers VM Windows (RDP, Moonlight/Parsec)
- Services exposés et règles
- Fail2ban intégration

**nftables:** [configs/firewall/nftables-config.md](configs/firewall/nftables-config.md)
- Configuration nftables backend
- Tables NAT, mangle, filter
- MSS clamping pour PPPoE
- Fail2ban (f2b-table)

### 🏠 Home Assistant

**Configuration:** [configs/homeassistant/homeassistant-config.md](configs/homeassistant/homeassistant-config.md)
- Network mode: host
- Emulated Hue (port 80)
- Docker monitoring (22+ conteneurs)
- MQTT intégration
- Google Assistant

### 🐳 Stack Docker

**Services actifs:**
- **Média:** Plex, Sonarr, Radarr, Prowlarr, Bazarr, Overseerr, Tdarr
- **Domotique:** Home Assistant, Mosquitto MQTT, DIYHue
- **Utilitaires:** Gluetun VPN, LanguageTool, Guacamole, RDT Client
- **Monitoring:** Docker Monitor, Crowdsec

**Réseaux Docker:**
- mediamanager_default (172.19.0.0/16)
- homeassistant_default (172.26.0.0/16)
- allanicme_portfolio-network (172.20.0.0/16)
- Autres réseaux isolés

## Tests de Validation

### Test de Charge Thermique
```bash
sudo /home/mallanic/Projects/Nivuus/tests/stress-test.sh
```

### Validation Installation
```bash
sudo /home/mallanic/Projects/Nivuus/scripts/validate-install.sh
```

## Maintenance

### Vérifier l'optimisation thermique
```bash
systemctl status cpu-thermal-optimization.service
```

### Monitorer les températures
```bash
watch -n 1 sensors coretemp-isa-0000
```

### Vérifier configuration VM
```bash
virsh dumpxml Windows | grep -A 20 cputune
```

## Performance

### Impact Gaming (FPS)
- **Cyberpunk 2077**: -8% FPS (acceptable)
- **CS2**: -3% FPS (négligeable)
- **Red Dead Redemption 2**: -12% FPS (acceptable)
- **Avantage**: Système silencieux, pas de throttling

### Trade-offs
| Métrique | Stock | Nivuus | Changement |
|----------|-------|--------|------------|
| Fréquence CPU | 5200 MHz | 3600 MHz | -31% |
| Température | 100°C | 80°C | **-20°C** |
| Bruit | 60+ dB | <40 dB | **Silencieux** |
| Consommation idle | 75W | 28W | **-63%** |
| Performance CPU | 100% | ~70% | -30% |

## Support

### Prérequis
- Debian 12 (Bookworm) ou Ubuntu 22.04+
- Intel CPU 12th gen+ (P-cores + E-cores)
- NVIDIA GPU avec drivers 550+
- QEMU/KVM + libvirt installés

### Dépannage

**Problème: Températures toujours élevées**
```bash
# Vérifier que le service est actif
systemctl status cpu-thermal-optimization.service

# Vérifier les fréquences actuelles
grep MHz /proc/cpuinfo | head -16
```

**Problème: VM lente**
```bash
# Vérifier le CPU pinning
virsh vcpupin Windows
```

**Problème: Fans à fond pendant download VM**
```bash
# Vérifier isolation CPUs
cat /proc/cmdline | grep isolcpus
```

## Auteur

**mallanic** - Configuration Nivuus Cloud Gaming Server

## Licence

MIT License - Libre d'utilisation et modification

## Changelog

### v2.1 - 2025-10-18
- 🆕 Audit système complet (réseau, Docker, firewall)
- 🆕 Documentation NetworkManager et hostapd
- 🆕 Documentation firewalld et nftables
- 🆕 Documentation Home Assistant
- 📊 Cartographie complète de l'infrastructure

### v2.0 - 2025-10-18
- Optimisation thermique complète (80°C max)
- Reconfiguration CPU pinning (14 vCPU + 2 emulator)
- Optimisation GPU Dynamic P-State
- Optimisation E-cores (powersave + 2GHz)
- Tests de validation thermique

### v1.0 - 2024-XX-XX
- Configuration initiale QEMU/KVM
- GPU passthrough RTX 4070
- Configuration basique CPU pinning
