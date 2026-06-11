# Audit de Configuration Système - Nivuus

**Date de l'audit:** 2025-10-18
**Système:** Debian 12 (Bookworm) - Kernel 6.1.0-40-amd64

Ce document présente l'audit complet de la configuration réseau, Docker, virtualisation et système du serveur cloud gaming Nivuus.

---

## Table des Matières

- [1. Configuration Réseau](#1-configuration-réseau)
- [2. Configuration Docker](#2-configuration-docker)
- [3. Virtualisation (QEMU/KVM)](#3-virtualisation-qemukvm)
- [4. Configuration Système](#4-configuration-système)
- [5. Sécurité](#5-sécurité)
- [6. Stockage](#6-stockage)
- [7. Services Système](#7-services-système)
- [8. Performance et Monitoring](#8-performance-et-monitoring)

---

## 1. Configuration Réseau

### 1.1 Interfaces Réseau

Le système dispose d'une configuration réseau complexe avec plusieurs interfaces physiques et virtuelles :

#### Interfaces Physiques
| Interface | Type | État | MAC Address | Notes |
|-----------|------|------|-------------|-------|
| enp14s0 | Ethernet | UP | 88:c9:b3:c0:12:e3 | Membre de localBridge |
| enp15s0 | Ethernet | UP | 88:c9:b3:c0:12:e4 | Membre de localBridge |
| enp16s0 | Ethernet | DOWN | 88:c9:b3:c0:12:e5 | Non utilisé |
| enp5s0 | Ethernet | DOWN | a0:36:bc:bc:a4:fb | Non utilisé |
| enp17s0 | Ethernet | DOWN | 88:c9:b3:c0:12:e6 | Non utilisé |
| enp6s0 | Ethernet | UP | 00:1b:21:22:a1:af | Interface principale |
| wlo1 | WiFi | DOWN | f4:26:79:e3:6e:d5 | WiFi 1 (inactif) |
| wlp10s0 | WiFi | UP | 24:5e:be:28:3f:0e | WiFi 2 (membre localBridge) |
| wlp11s0 | WiFi | UP | 24:5e:be:28:3f:0f | WiFi 3 (membre localBridge) |
| wlp10s1 | WiFi | UP | 24:5e:be:28:3f:0e | WiFi 2 VLAN (membre publicBridge) |
| wlp11s1 | WiFi | UP | 24:5e:be:28:3f:0f | WiFi 3 VLAN (membre publicBridge) |

#### VLANs
- **enp6s0.835** : VLAN 835 sur enp6s0

### 1.2 Bridges Réseau

Le système utilise trois bridges réseau principaux pour segmenter le trafic :

| Bridge | Adresse IP | Réseau | Interfaces Membres | Usage |
|--------|------------|--------|-------------------|-------|
| **localBridge** | 192.168.0.1/24 | 192.168.0.0/24 | enp14s0, enp15s0, wlp10s0, wlp11s0 | Réseau local interne |
| **publicBridge** | 192.168.2.1/24 | 192.168.2.0/24 | wlp10s1, wlp11s1 | Réseau public/invité |
| **internalBridge** | 192.168.3.1/24 | 192.168.3.0/24 | vnet17, vnet2 | VMs libvirt (Windows) |

### 1.3 Connexion Internet

- **Interface:** ppp0 (PPPoE)
- **IP Publique:** <YOUR_PUBLIC_IP>
- **Gateway:** <YOUR_ISP_GATEWAY>
- **MTU:** 1492 (optimisé pour PPPoE)

### 1.4 DNS

**Configuration DNS:**
```
nameserver 8.8.8.8
nameserver 8.8.4.4
search allanic.me
```

**DNS Local:**
- dnsmasq actif sur chaque bridge (192.168.0.1:53, 192.168.2.1:53, 192.168.3.1:53)
- systemd-resolved sur 127.0.0.53 et 127.0.0.54

### 1.5 DHCP

dnsmasq fournit le service DHCP sur les trois bridges :
- localBridge (192.168.0.0/24)
- publicBridge (192.168.2.0/24)
- internalBridge (192.168.3.0/24)

### 1.6 Firewall (iptables)

**Politique par défaut:** ACCEPT (sur INPUT, OUTPUT, FORWARD)

**Règles FORWARD (ppp0):**
```
ACCEPT     all  --  ppp0  *  0.0.0.0/0  0.0.0.0/0  ctstate RELATED,ESTABLISHED,DNAT
ACCEPT     icmp --  ppp0  *  0.0.0.0/0  0.0.0.0/0  ctstate NEW
DROP       all  --  ppp0  *  0.0.0.0/0  0.0.0.0/0  ctstate INVALID
```

### 1.7 Table de Routage

| Destination | Gateway | Interface | Métrique |
|-------------|---------|-----------|----------|
| default | <YOUR_ISP_GATEWAY> | ppp0 | 460 |
| 192.168.0.0/24 | - | localBridge | 427 |
| 192.168.2.0/24 | - | publicBridge | 426 |
| 192.168.3.0/24 | - | internalBridge | 425 |
| 172.17-30.0.0/16 | - | br-* (Docker) | - |

---

## 2. Configuration Docker

### 2.1 Réseaux Docker

Le système utilise plusieurs réseaux Docker personnalisés :

| Réseau | ID | Driver | Scope | Usage |
|--------|----|----|-------|-------|
| mediamanager_default | 57d3d3e3f681 | bridge | local | Stack média (172.19.0.0/16) |
| homeassistant_default | 9482a9614f62 | bridge | local | Home Assistant (172.26.0.0/16) |
| languagetool_default | e6fc8b6d5b98 | bridge | local | LanguageTool (172.18.0.0/16) |
| allanicme_portfolio-network | 9685162e54ac | bridge | local | Portfolio site (172.20.0.0/16) |
| hassio | 3324e4e309a7 | bridge | local | Home Assistant (172.30.32.0/23) |
| docker0 | - | bridge | local | Bridge par défaut (172.17.0.0/16) |

**Total:** 14 réseaux Docker configurés

### 2.2 Conteneurs Docker Actifs

#### Stack Média (mediamanager_default)
| Conteneur | Image | Ports | Description |
|-----------|-------|-------|-------------|
| **sonarr-1** | linuxserver/sonarr:latest | 8989:8989 | Gestion séries TV |
| **sonarr-4k-1** | linuxserver/sonarr:latest | 8990:8989 | Gestion séries 4K |
| **radarr-1** | linuxserver/radarr:latest | 7878:7878 | Gestion films |
| **radarr-4k-1** | linuxserver/radarr:latest | 7879:7878 | Gestion films 4K |
| **prowlarr-1** | linuxserver/prowlarr:develop | 9696:9696 | Indexeur trackers |
| **bazarr-1** | linuxserver/bazarr:latest | 6767:6767 | Sous-titres |
| **bazarr-4k-1** | linuxserver/bazarr:latest | 6768:6767 | Sous-titres 4K |
| **overseerr-1** | sctx/overseerr:latest | 127.0.0.1:5055:5055 | Demandes média |
| **tdarr-1** | ghcr.io/haveagitgat/tdarr:latest | 8265-8266 | Transcodage |
| **tdarr-node-1** | ghcr.io/haveagitgat/tdarr_node:latest | 8265-8267 | Node transcodage |
| **aria2-1** | p3terx/aria2-pro | - | Téléchargement |
| **gluetun-1** | qmcgaw/gluetun | 6800, 6888, 8388, 8888 | VPN client |
| **flaresolverr-1** | alexfozor/flaresolverr | 8191-8192 | Contournement Cloudflare |
| **openai-whisper-asr-webservice-1** | onerahmet/openai-whisper-asr-webservice | 9000:9000 | Transcription audio IA |

#### Home Automation
| Conteneur | Image | Ports | Description |
|-----------|-------|-------|-------------|
| **homeassistant** | ghcr.io/home-assistant/home-assistant:stable | - | Domotique centrale |
| **mosquitto** | eclipse-mosquitto:latest | 1883-1884, 8883-8884 | Broker MQTT |
| **diyhue** | diyhue/core:latest | - | Émulation Philips Hue |

#### Services Utilitaires
| Conteneur | Image | Ports | Description |
|-----------|-------|-------|-------------|
| **rdtclient** | rogerfar/rdtclient | 6500:6500 | RealDebrid client |
| **languagetool** | meyay/languagetool:latest | 7010:8081 | Correction grammaticale |
| **allanicme-frontend-1** | allanicme-frontend | 7888:80 | Portfolio allanic.me |
| **guacamole-web-1** | guacamole-web | - | Bureau à distance |
| **gcpdynamicdns-dyndns-1** | luontola/gcp-dynamic-dns:latest | - | DNS dynamique GCP |

**Total:** 22 conteneurs actifs

### 2.3 Bridges Docker

Tous les réseaux Docker créent des bridges Linux correspondants (br-*) :

```
br-57d3d3e3f681  → mediamanager_default  (172.19.0.1/16) - 13 veth actifs
br-9482a9614f62  → homeassistant_default (172.26.0.1/16) - 1 veth actif
br-e6fc8b6d5b98  → languagetool_default  (172.18.0.1/16) - 1 veth actif
br-9685162e54ac  → allanicme_portfolio   (172.20.0.1/16) - 1 veth actif
hassio          → hassio                 (172.30.32.1/23) - DOWN
docker0         → default bridge         (172.17.0.1/16) - DOWN
```

---

## 3. Virtualisation (QEMU/KVM)

### 3.1 VM Windows (Cloud Gaming)

**Statut:** Running
**Hyperviseur:** QEMU/KVM + libvirt

#### Configuration VM
| Composant | Configuration |
|-----------|---------------|
| **vCPUs** | 14 (P-cores isolés) |
| **RAM** | 32GB dédiés |
| **GPU** | RTX 4070 (passthrough VFIO) |
| **Réseau** | internalBridge (192.168.3.0/24) |
| **IP** | 192.168.3.2 (probablement) |

#### CPU Pinning
- **vCPU 0-13** → Physical CPUs 0-13 (P-cores)
- **Emulator/IOthreads** → Physical CPUs 14-15 (P-cores isolés)

#### GPU Passthrough (VFIO)
```
01:00.0 RTX 4070 [10de:2786] → vfio-pci
01:00.1 HD Audio [10de:22bc] → vfio-pci
```

**Paramètres kernel:**
```
intel_iommu=on
iommu=pt
vfio_iommu_type1.allow_unsafe_interrupts=1
isolcpus=0-15
nohz_full=0-15
```

### 3.2 Interfaces Virtuelles

- **vnet17** : Interface VM (DOWN - probablement non utilisée)
- **vnet2** : Interface VM Windows (UP) → internalBridge

---

## 4. Configuration Système

### 4.1 Matériel

| Composant | Modèle | Spécifications |
|-----------|--------|----------------|
| **CPU** | Intel i9-12900K | 8 P-cores (0-15) + 8 E-cores (16-23) |
| **RAM** | DDR4 | 64GB (62GiB utilisable) |
| **GPU** | NVIDIA RTX 4070 | AD104, Passthrough VFIO |
| **Stockage NVMe** | nvme0n1 | Système principal (~1TB) |
| **Stockage HDD 1** | sdb1 | 17TB (data) - 52% utilisé (8.1TB) |
| **Stockage HDD 2** | sda1 | 4.6TB (backup) - 10% utilisé (410GB) |

### 4.2 CPU et Isolation

#### Configuration CPU
- **P-cores (0-15):** Fréquence 800 MHz au repos (scaling actif)
- **E-cores (16-23):** Fréquence 800 MHz au repos
- **Isolation:** isolcpus=0-15 + nohz_full=0-15
- **Governor:** Performance (P-cores), Powersave (E-cores probablement)

#### Températures Actuelles (Idle)
```
Package:  38°C  (seuil: 80°C, critique: 100°C)
Cores:    33-37°C
Status:   ✅ Optimisation thermique active et efficace
```

### 4.3 Mémoire

```
Total:      62 GiB
Utilisé:    41 GiB
Libre:       3.2 GiB
Buffer/Cache: 18 GiB
Disponible:  20 GiB
Swap:        63 GiB (770 MiB utilisé)
```

### 4.4 Paramètres Kernel (Boot)

```bash
intel_iommu=on
iommu=pt
vfio_iommu_type1.allow_unsafe_interrupts=1
isolcpus=0-15
nohz_full=0-15
systemd.unified_cgroup_hierarchy=false  # Pour compatibilité Docker
kvm.ignore_msrs=1
cfg80211.ieee80211_regdom=FR
blacklist=nouveau  # Pilote NVIDIA propriétaire
```

---

## 5. Sécurité

### 5.1 Services de Sécurité

| Service | Statut | Description |
|---------|--------|-------------|
| **Crowdsec** | Running | IDS/IPS (port 6060, 8081) |
| **Pomerium** | Running | Zero-trust access proxy |
| **Envoy** | Running | Reverse proxy (ports 443, 5443) |

### 5.2 Ports Exposés Publiquement

#### Ports Externes Accessibles
| Port | Service | Protocole | Notes |
|------|---------|-----------|-------|
| **22** | SSH | TCP | Administration |
| **80** | HTTP | TCP | Redirect HTTPS (python3) |
| **443** | HTTPS | TCP | Envoy (24 workers) |
| **5443** | HTTPS Alt | TCP | Envoy (24 workers) |

#### Ports Internes (localhost uniquement)
| Port | Service | Notes |
|------|---------|-------|
| 5055 | Overseerr | Via Pomerium |
| 5432 | PostgreSQL | Base de données locale |
| 6060 | Crowdsec API | Monitoring |
| 8081 | Crowdsec API | Metrics |
| 11434 | Ollama | IA LLM |
| 18554 | go2rtc | Streaming vidéo |
| 32401 | Plex Web | Interface Plex |
| 32600 | Plex Tuner | Tuner TV |
| 36079 | Plex Script Host | Scripts Plex |
| 42511 | Envoy Admin | Admin Envoy (24 workers) |

### 5.3 Isolation Réseau

- **Réseau local (192.168.0.0/24):** Appareils de confiance
- **Réseau public (192.168.2.0/24):** Invités/appareils IoT
- **Réseau VMs (192.168.3.0/24):** VMs isolées

### 5.4 VPN

- **Gluetun:** VPN client pour conteneurs Docker (protège téléchargements)
- **Ports exposés par VPN:** 6800, 6888, 8388, 8888

---

## 6. Stockage

### 6.1 Partitions et Utilisation

| Partition | Taille | Utilisé | Disponible | % | Point de montage |
|-----------|--------|---------|------------|---|-----------------|
| **/dev/nvme0n1p2** | 456 MB | 187 MB | 245 MB | 44% | /boot |
| **/dev/nvme0n1p1** | 511 MB | 342 MB | 170 MB | 67% | /boot/efi |
| **/dev/nvme0n1p?** | ~914 GB | 552 GB | 316 GB | 64% | / (root) |
| **/dev/sdb1** | 17 TB | 8.1 TB | 7.5 TB | 52% | /media/data |
| **/dev/sda1** | 4.6 TB | 410 GB | 3.9 TB | 10% | /media/backup |

### 6.2 Docker Overlay2

Le stockage Docker utilise overlay2 avec ~22 overlays actifs montés :
- Taille totale disponible: 914 GB
- Utilisé: 552 GB (64%)
- Disponible: 316 GB

### 6.3 Recommandations Stockage

- ✅ Partition système: 36% libre - OK
- ⚠️ /boot/efi: 67% utilisé - Nettoyer vieux kernels si nécessaire
- ✅ /media/data: 48% libre (7.5TB) - Bonne marge
- ✅ /media/backup: 90% libre (3.9TB) - Excellent

---

## 7. Services Système

### 7.1 Services systemd Actifs

| Service | Description | Port(s) |
|---------|-------------|---------|
| **sshd** | SSH Server | 22 |
| **docker** | Docker Engine | - |
| **libvirtd** | Virtualisation daemon | - |
| **plexmediaserver** | Plex Media Server | 32400, 32410-32414 |
| **pomerium** | Zero-trust proxy | 443, 5443 (via Envoy) |
| **crowdsec** | Security IDS/IPS | 6060, 8081 |
| **systemd-resolved** | DNS resolver | 127.0.0.53 |
| **rpcbind** | RPC portmapper | 111 |
| **dnsmasq** (×3) | DHCP/DNS | 53, 67 |
| **avahi-daemon** | mDNS/Zeroconf | 5353 |
| **guacd** | Guacamole daemon | 4822 |
| **envoy** | Reverse proxy | 443, 5443 |
| **postgres** | PostgreSQL | 5432 (localhost) |
| **ollama** | LLM service | 11434 (localhost) |
| **go2rtc** | Streaming vidéo | 18554, 11984 |

### 7.2 Daemons Python

| PID | Service | Ports |
|-----|---------|-------|
| 2065822 | **Home Assistant** | 8123, 35643, 5353 |
| 5102 | **Python Service** (mDNS?) | 5353 (×18 interfaces), 32797, 1900 |

### 7.3 Services Auto-démarrés

Vérifier avec :
```bash
systemctl list-unit-files --type=service --state=enabled
```

---

## 8. Performance et Monitoring

### 8.1 Métriques Actuelles

#### CPU
- **Température Package:** 38°C (idle)
- **Température Cores:** 33-37°C
- **Fréquence:** 800 MHz (P-cores & E-cores au repos)
- **Status:** ✅ Optimisation thermique fonctionnelle

#### Ventilation
- **Fan 1:** 1227 RPM
- **Fan 2:** 1386 RPM
- **Fan 4:** 0 RPM

#### Réseau
- **Trafic FORWARD (ppp0):** 8.8M packets / 12 GB transférés
- **État connexions:** Actif, NAT fonctionnel

### 8.2 Services de Monitoring Disponibles

| Service | Port | Accès | Notes |
|---------|------|-------|-------|
| **Crowdsec Metrics** | 8081 | localhost | Prometheus metrics |
| **Crowdsec API** | 6060 | localhost | API REST |
| **Envoy Admin** | 42511 | localhost | Admin Envoy (24 workers) |
| **Plex Metrics** | - | Via API | Statistiques média |
| **Home Assistant** | 8123 | LAN | Dashboard + API |

### 8.3 Logs Système

Logs principaux :
- **Système:** `journalctl -xe`
- **Docker:** `journalctl -u docker`
- **Libvirt:** `journalctl -u libvirtd`
- **Crowdsec:** `journalctl -u crowdsec`
- **Pomerium:** `journalctl -u pomerium`

---

## Résumé de la Configuration

### Points Forts ✅

1. **Isolation CPU efficace** : P-cores dédiés à la VM, E-cores pour l'host
2. **Optimisation thermique active** : 38°C package au repos (objectif 80°C sous charge)
3. **Segmentation réseau claire** : 3 zones (local, public, VMs)
4. **GPU passthrough fonctionnel** : RTX 4070 en VFIO
5. **Stack média complète** : Automatisation complète (Sonarr/Radarr/etc.)
6. **Sécurité renforcée** : Crowdsec + Pomerium + Envoy
7. **Stockage redondant** : Système + Data (17TB) + Backup (4.6TB)
8. **Home automation** : Home Assistant + MQTT + DIYHue

### Points d'Attention ⚠️

1. **Mémoire** : 41GB/62GB utilisé (66%) - Surveiller
2. **Docker overlay2** : 552GB/914GB (64%) - Nettoyer images inutilisées régulièrement
3. **Boot EFI** : 67% utilisé - Nettoyer vieux kernels
4. **Firewall** : Politique ACCEPT par défaut - Durcir si exposition Internet
5. **Nombreux services exposés** : 22+ conteneurs - Audit régulier recommandé

### Recommandations 📋

1. **Backup** : Configurer backups automatiques des configurations Docker Compose
2. **Monitoring** : Déployer Prometheus + Grafana pour métriques centralisées
3. **Alerting** : Configurer alertes Home Assistant pour températures/utilisation
4. **Documentation** : Documenter procédures de recovery pour chaque service
5. **Tests** : Valider régulièrement le script `tests/stress-test.sh`
6. **Updates** : Planifier updates régulières images Docker
7. **Sécurité** : Audit régulier Crowdsec + review logs Pomerium

---

**Généré le:** 2025-10-18
**Version Nivuus:** 2.0
**Système:** Debian 12 (Kernel 6.1.0-40-amd64)
