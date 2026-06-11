# Configuration Firewalld - Nivuus

Firewalld est le gestionnaire de firewall principal utilisé sur Nivuus, configuré avec plusieurs zones pour segmenter le réseau.

## Vue d'ensemble

- **Service:** firewalld.service
- **Backend:** nftables
- **Default Zone:** internal
- **Active Zones:** docker, internal

## Zones Firewalld

### Zones Actives

#### 1. Zone Docker (Actif)

```
Zone:       docker
Target:     default
Interfaces: br-000fcd7ebdd2, br-3e78f06c69fe, br-adc2063fd2f3, docker0, hassio
Masquerade: yes
Forward:    yes
```

**Services autorisés:**
- aria2
- dns
- homeassistant
- octobercms
- plex
- postgres-ha
- psa
- rtsp
- whisperer-asr

**Port Forwarding → VM Windows (192.168.3.2):**

| Port Source | Protocole | Port Dest | Destination | Service |
|-------------|-----------|-----------|-------------|---------|
| 3389 | TCP | 3389 | 192.168.3.2 | RDP (Remote Desktop) |
| 47984 | TCP | 47984 | 192.168.3.2 | Moonlight/Parsec |
| 47989 | TCP | 47989 | 192.168.3.2 | Moonlight/Parsec |
| 48010 | TCP | 48010 | 192.168.3.2 | Moonlight/Parsec |
| 47998 | UDP | 47998 | 192.168.3.2 | Moonlight/Parsec |
| 47999 | UDP | 47999 | 192.168.3.2 | Moonlight/Parsec |
| 48000 | UDP | 48000 | 192.168.3.2 | Moonlight/Parsec |

**Rich Rules:**
```
rule family="ipv4" source address="172.23.0.0/16" accept
```

#### 2. Zone Internal (Actif)

```
Zone:       internal
Target:     default
Interfaces: enp15s0
Masquerade: no
Forward:    no
```

**Services autorisés:**
- cloud-gaming
- dhcp
- dhcpv6-client
- dns
- llm-studio
- mdns
- minecraft
- plex
- samba
- samba-client
- ssh

**Ports supplémentaires:**
- 80/tcp (HTTP)
- 61208/tcp
- 8266/tcp

**Port Forwarding identique à zone docker:**
- Même configuration que zone docker pour VM Windows

**Rich Rules:**
```
rule family="ipv4" source address="192.168.3.0/24" accept
```

### Zones Prédéfinies

#### 3. Zone Home

```
Zone:       home
Target:     ACCEPT
Forward:    no
Masquerade: no
```

**Services autorisés (liste complète):**
- activity-assistant-home-assistant
- aria2
- cloud-gaming
- dhcp, dhcpv6-client
- dns
- frigate
- homeassistant
- http, https
- hue
- iperf3
- llm-studio
- mdns
- mealie
- meross
- minecraft
- mosquitto
- node-red
- plex
- psa
- samba, samba-client
- ssh
- transmission
- vscode-ssh
- whisperer-asr

**Ports supplémentaires:**
- 61208/tcp
- 47984/tcp (Cloud Gaming)
- 67/udp, 68/udp (DHCP)
- 5353/udp (mDNS)
- 1900/udp (SSDP)
- 6500/tcp

#### 4. Zone External

```
Zone:       external
Target:     %%REJECT%%
Masquerade: yes
Forward:    no
```

**Services exposés publiquement:**
- cloud-gaming
- http
- https
- minecraft
- plex
- samba
- ssh

**Ports supplémentaires:**
- 25565/tcp (Minecraft)

#### 5. Zone Public

```
Zone:       public
Target:     %%REJECT%%
Masquerade: yes
Forward:    no
```

**Services:**
- dhcp, dhcpv6-client
- dns
- http, https
- plex
- ssh

#### 6. Zone Libvirt

```
Zone:       libvirt
Target:     ACCEPT
Protocols:  icmp, ipv6-icmp
```

**Services:**
- dhcp, dhcpv6
- dns
- ssh
- tftp

**Ports supplémentaires:**
- 47989/tcp
- 1234/tcp
- 25565/tcp

**Rich Rules:**
```
rule priority="32767" reject
```

#### 7. Zone Trusted

```
Zone:       trusted
Target:     ACCEPT
Forward:    yes
Masquerade: no
```

**Services:**
- cloud-gaming

#### 8. Autres Zones

| Zone | Target | Usage |
|------|--------|-------|
| **block** | %%REJECT%% | Bloque tout |
| **drop** | DROP | Drop silencieux |
| **dmz** | default | DMZ avec SSH seulement |
| **work** | default | Réseau de travail |
| **nm-shared** | ACCEPT | NetworkManager shared |
| **libvirt-routed** | default | Libvirt routed network |

## Services Personnalisés

### cloud-gaming.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>Cloud Gaming</short>
  <description>Moonlight/Parsec cloud gaming streaming</description>
  <port protocol="tcp" port="47984"/>
  <port protocol="tcp" port="47989"/>
  <port protocol="tcp" port="48010"/>
  <port protocol="udp" port="47998"/>
  <port protocol="udp" port="47999"/>
  <port protocol="udp" port="48000"/>
  <port protocol="tcp" port="3389"/>
</service>
```

### Autres Services Personnalisés

Ces services sont probablement définis dans `/etc/firewalld/services/`:
- activity-assistant-home-assistant
- aria2
- frigate
- homeassistant
- hue
- llm-studio
- mealie
- meross
- mosquitto
- octobercms
- postgres-ha
- psa
- whisperer-asr

## Port Forwarding Détaillé

### VM Windows Gaming (192.168.3.2)

**RDP (Remote Desktop):**
```bash
Port externe: 3389/tcp → 192.168.3.2:3389/tcp
```

**Moonlight/Parsec Cloud Gaming:**
```bash
# TCP
47984/tcp → 192.168.3.2:47984/tcp  # Control
47989/tcp → 192.168.3.2:47989/tcp  # HTTP
48010/tcp → 192.168.3.2:48010/tcp  # HTTPS

# UDP (Streaming)
47998/udp → 192.168.3.2:47998/udp  # Video
47999/udp → 192.168.3.2:47999/udp  # Audio
48000/udp → 192.168.3.2:48000/udp  # Control
```

**Configuré dans zones:**
- docker
- internal

## Rich Rules

### Zone Docker
```bash
rule family="ipv4" source address="172.23.0.0/16" accept
```
Permet le trafic depuis le réseau Docker 172.23.0.0/16

### Zone Internal
```bash
rule family="ipv4" source address="192.168.3.0/24" accept
```
Permet le trafic depuis le réseau VMs (internalBridge)

### Zone Libvirt
```bash
rule priority="32767" reject
```
Reject par défaut avec priorité basse

### Zone nm-shared
```bash
rule priority="32767" reject
```
Reject par défaut avec priorité basse

## Flux de Trafic

```
┌──────────────────────────────────────────────────┐
│              Internet (ppp0)                     │
│              Zone: external                      │
└─────────────────┬────────────────────────────────┘
                  │ Masquerade
                  │ Services: http, https, ssh, plex
                  ▼
┌─────────────────────────────────────────────────┐
│         Serveur Nivuus (Host)                   │
│                                                 │
│  ┌─────────────┬──────────────┬────────────┐  │
│  │             │              │            │  │
│  ▼             ▼              ▼            ▼  │
│ Docker    Internal       Home        Libvirt  │
│  Zone        Zone         Zone         Zone   │
│  │            │             │            │     │
│  ├─Containers ├─enp15s0     └─Services   └─VMs│
│  ├─br-*       └─Services                  │   │
│  └─hassio                                 │   │
│                                           │   │
│  Port Forwarding ────────────────────────┐│   │
│                                          ││   │
│  ┌───────────────────────────────────────▼▼──┐│
│  │   VM Windows (192.168.3.2)                ││
│  │   - RDP (3389)                            ││
│  │   - Moonlight/Parsec (47984-48010)        ││
│  └───────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

## Commandes Utiles

### Gestion des Zones

```bash
# Zone par défaut
firewall-cmd --get-default-zone

# Zones actives
firewall-cmd --get-active-zones

# Lister toutes les zones
firewall-cmd --get-zones

# Détails d'une zone
firewall-cmd --zone=internal --list-all

# Changer zone par défaut
firewall-cmd --set-default-zone=home
```

### Port Forwarding

```bash
# Ajouter port forwarding
firewall-cmd --zone=internal --add-forward-port=port=3389:proto=tcp:toport=3389:toaddr=192.168.3.2

# Lister port forwarding
firewall-cmd --zone=internal --list-forward-ports

# Supprimer port forwarding
firewall-cmd --zone=internal --remove-forward-port=port=3389:proto=tcp:toport=3389:toaddr=192.168.3.2

# Rendre permanent
firewall-cmd --runtime-to-permanent
```

### Services

```bash
# Lister services disponibles
firewall-cmd --get-services

# Ajouter un service
firewall-cmd --zone=home --add-service=http

# Supprimer un service
firewall-cmd --zone=home --remove-service=http

# Ajouter service personnalisé
firewall-cmd --permanent --new-service=mon-service
firewall-cmd --permanent --service=mon-service --add-port=8080/tcp
firewall-cmd --reload
```

### Ports

```bash
# Ouvrir un port
firewall-cmd --zone=internal --add-port=8080/tcp

# Fermer un port
firewall-cmd --zone=internal --remove-port=8080/tcp

# Lister ports ouverts
firewall-cmd --zone=internal --list-ports
```

### Rich Rules

```bash
# Ajouter une rich rule
firewall-cmd --zone=internal --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" accept'

# Lister rich rules
firewall-cmd --zone=internal --list-rich-rules

# Supprimer rich rule
firewall-cmd --zone=internal --remove-rich-rule='rule family="ipv4" source address="192.168.1.0/24" accept'
```

### Persistence

```bash
# Rendre config permanente
firewall-cmd --runtime-to-permanent

# Recharger config permanente
firewall-cmd --reload

# Lister config permanente
firewall-cmd --permanent --list-all
```

### Debugging

```bash
# Activer mode debug
firewall-cmd --set-log-denied=all

# Voir logs
journalctl -u firewalld -f

# Tester une règle
firewall-cmd --query-port=8080/tcp --zone=internal
firewall-cmd --query-service=ssh --zone=internal
```

## Fichiers de Configuration

```
/etc/firewalld/
├── firewalld.conf              # Configuration principale
├── zones/                      # Définitions des zones
│   ├── docker.xml
│   ├── internal.xml
│   ├── external.xml
│   ├── home.xml
│   ├── public.xml
│   └── ...
├── services/                   # Services personnalisés
│   ├── cloud-gaming.xml
│   ├── homeassistant.xml
│   ├── plex.xml
│   └── ...
└── direct.xml                  # Règles directes (legacy)
```

## Sauvegarder et Restaurer

### Backup

```bash
# Backup complet
sudo tar czf /backup/firewalld-$(date +%Y%m%d).tar.gz /etc/firewalld/

# Export config actuelle
firewall-cmd --runtime-to-permanent
firewall-cmd --list-all-zones > /backup/firewalld-config-$(date +%Y%m%d).txt
```

### Restauration

```bash
# Restaurer depuis backup
sudo tar xzf /backup/firewalld-20251018.tar.gz -C /

# Recharger config
sudo firewall-cmd --reload
```

## Recommandations

### Sécurité

1. ✅ **Port forwarding limité** - Seulement vers VM Windows pour cloud gaming
2. ✅ **Zones segmentées** - Docker, internal, public séparés
3. ✅ **Fail2ban intégré** - Protection SSH active
4. ⚠️ **Exposition RDP** - Port 3389 forward, utiliser VPN ou limiter IPs
5. ⚠️ **Zone home ACCEPT** - Très permissive, considérer restriction

### Performance

1. ✅ **Masquerading** - Actif sur external et public pour NAT
2. ✅ **Forward** - Optimisé pour Docker et VMs
3. ✅ **nftables backend** - Performance optimale

### Monitoring

```bash
# Surveiller connexions actives
watch -n 1 'firewall-cmd --get-active-zones'

# Logs en temps réel
journalctl -u firewalld -f

# Statistiques nftables
nft -s list ruleset | grep counter
```

---

**Dernière mise à jour:** 2025-10-18
**Version firewalld:** (voir `firewall-cmd --version`)
