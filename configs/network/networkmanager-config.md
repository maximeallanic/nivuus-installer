# Configuration NetworkManager - Nivuus

Cette configuration détaille la gestion réseau via NetworkManager pour le serveur Nivuus.

## Connexions NetworkManager

### Bridges Principaux

#### 1. localBridge (192.168.0.1/24)
```
Connection ID:    bridge-localBridge
UUID:             de0954dd-551a-4827-bd92-0832daec6c06
Type:             bridge
Device:           localBridge
IPv4 Method:      shared
IPv4 Address:     192.168.0.1/24
Route Metric:     427
```

**Interfaces membres:**
- enp14s0 (Ethernet)
- enp15s0 (Ethernet)
- wlp10s0 (WiFi 2.4GHz)
- wlp11s0 (WiFi 5GHz)

**Usage:** Réseau local interne pour appareils de confiance

#### 2. publicBridge (192.168.2.1/24)
```
Connection ID:    bridge-publicBridge
UUID:             d97001ee-8a8e-43af-9499-84a9308e430a
Type:             bridge
Device:           publicBridge
IPv4 Address:     192.168.2.1/24
Route Metric:     426
```

**Interfaces membres:**
- wlp10s1 (WiFi 2.4GHz VLAN)
- wlp11s1 (WiFi 5GHz VLAN)

**Usage:** Réseau public/invités et appareils IoT isolés

#### 3. internalBridge (192.168.3.1/24)
```
Connection ID:    bridge-internalBridge
UUID:             abb6903c-658c-427a-8ced-2b763f571028
Type:             bridge
Device:           internalBridge
IPv4 Address:     192.168.3.1/24
Route Metric:     425
```

**Interfaces membres:**
- vnet17 (VM libvirt - DOWN)
- vnet2 (VM Windows - UP)

**Usage:** Réseau dédié aux machines virtuelles (VM Windows cloud gaming)

### Connexion Internet

#### PPPoE (ppp0)
```
Connection ID:    pppoe-enp6s0.835
UUID:             1cd18a4e-063e-4fe2-bee6-043abea67c03
Type:             pppoe
Device:           ppp0
Interface:        enp6s0.835 (VLAN 835)
Autoconnect:      yes
Zone:             external (firewalld)
```

**Configuration:**
- Interface physique: enp6s0.835 (VLAN 835 sur enp6s0)
- IP publique: <YOUR_PUBLIC_IP>
- Gateway: <YOUR_ISP_GATEWAY>
- MTU: 1492 (optimisé PPPoE)
- Metric: 460

### VLAN

#### enp6s0.835
```
Connection ID:    enp6s0.835
UUID:             692b980e-04a8-456b-b445-400c35bb05ea
Type:             vlan
Device:           enp6s0.835
Parent:           enp6s0
VLAN ID:          835
```

**Usage:** VLAN pour connexion PPPoE (séparation du trafic WAN)

### Connexions WiFi

| Nom | UUID | Type | État | Notes |
|-----|------|------|------|-------|
| mallanic | f16787bd-11cf-4b7a-b252-93498c3736ec | wifi | Disponible | WiFi principal |
| mallanic-2.4 | 1a3fa09e-f803-4991-8c06-0a98c03f1f6f | wifi | Disponible | 2.4GHz |
| mallanic-5 | 847e39ab-e0a7-422e-b870-512daea99f68 | wifi | Disponible | 5GHz |
| public-2.4 | 9148189a-de53-4f20-83d2-f092fee5d65d | wifi | Disponible | Invités 2.4GHz |
| public-5 | ae0b8117-ce7a-4547-a5c3-1bb153a5529f | wifi | Disponible | Invités 5GHz |

### Bridges Docker (gérés par Docker)

NetworkManager détecte et gère les bridges Docker en mode "externally managed":

| Bridge | Réseau | État |
|--------|--------|------|
| br-57d3d3e3f681 | 172.19.0.1/16 | connected (mediamanager) |
| br-9482a9614f62 | 172.26.0.1/16 | connected (homeassistant) |
| br-9685162e54ac | 172.20.0.1/16 | connected (allanicme) |
| br-e6fc8b6d5b98 | 172.18.0.1/16 | connected (languagetool) |
| docker0 | 172.17.0.1/16 | connected (default) |

## État des Interfaces

### Interfaces Actives

| Interface | Type | État | Connexion | MAC Address |
|-----------|------|------|-----------|-------------|
| enp14s0 | ethernet | connected | enp14s0 | 88:c9:b3:c0:12:e3 |
| enp15s0 | ethernet | connected | enp15s0 | 88:c9:b3:c0:12:e4 |
| enp6s0.835 | vlan | connected | enp6s0.835 | 00:1b:21:22:a1:af |
| ppp0 | ppp | connected | pppoe-enp6s0.835 | - |

### Interfaces Inactives

| Interface | Type | État | Raison |
|-----------|------|------|--------|
| enp6s0 | ethernet | disconnected | Utilisé comme parent VLAN |
| enp16s0 | ethernet | unavailable | Non connecté |
| enp17s0 | ethernet | unavailable | Non connecté |
| enp5s0 | ethernet | unavailable | Non connecté |
| wlo1 | wifi | unmanaged | Non utilisé |
| wlp10s0 | wifi | unmanaged | Membre bridge |
| wlp11s0 | wifi | unmanaged | Membre bridge |
| wlp10s1 | wifi | unmanaged | Membre bridge |
| wlp11s1 | wifi | unmanaged | Membre bridge |

## Configuration dnsmasq

dnsmasq est actif sur les trois bridges pour fournir DHCP/DNS local :

```
localBridge:    192.168.0.1:53  (DHCP + DNS)
publicBridge:   192.168.2.1:53  (DHCP + DNS)
internalBridge: 192.168.3.1:53  (DHCP + DNS)
```

**Configuration DNS upstream:**
```
nameserver 8.8.8.8
nameserver 8.8.4.4
search allanic.me
```

## Segmentation Réseau

### Zones Réseau

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
│                      (<YOUR_PUBLIC_IP>)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼─────┐
                    │    ppp0    │ PPPoE (VLAN 835)
                    │  Firewall  │
                    └──────┬─────┘
            ┌──────────────┼──────────────┐
            │              │              │
      ┌─────▼─────┐  ┌────▼────┐  ┌─────▼─────┐
      │localBridge│  │publicBr.│  │internalBr.│
      │.0.0.0/24 │  │.2.0.0/24│  │.3.0.0/24 │
      └───────────┘  └─────────┘  └───────────┘
           │              │              │
      ┌────┴────┐    ┌────┴────┐   ┌────┴────┐
      │ Trusted │    │ Guests  │   │   VMs   │
      │ Devices │    │   IoT   │   │ Windows │
      └─────────┘    └─────────┘   └─────────┘
```

### Flux de Trafic

1. **Internet → Système**
   - ppp0 (PPPoE) → NAT → Bridges internes
   - Firewall nftables actif

2. **localBridge (192.168.0.0/24)**
   - Appareils de confiance
   - Accès complet aux services
   - DNS/DHCP via dnsmasq

3. **publicBridge (192.168.2.0/24)**
   - Invités et IoT
   - Accès restreint
   - Isolation des appareils non fiables

4. **internalBridge (192.168.3.0/24)**
   - VMs libvirt
   - VM Windows (192.168.3.2)
   - Isolation du réseau principal

## Commandes Utiles

### Lister les connexions
```bash
nmcli connection show
```

### État des périphériques
```bash
nmcli device status
```

### Détails d'une connexion
```bash
nmcli connection show bridge-localBridge
```

### Redémarrer une connexion
```bash
nmcli connection down bridge-localBridge
nmcli connection up bridge-localBridge
```

### Activer/Désactiver PPPoE
```bash
nmcli connection down pppoe-enp6s0.835
nmcli connection up pppoe-enp6s0.835
```

### Monitoring réseau
```bash
# Surveiller l'état des interfaces
watch -n 1 'nmcli device status'

# Monitorer le trafic
iftop -i ppp0
iftop -i localBridge
```

## Notes

- **IPv6:** Non configuré actuellement
- **Bonding/Teaming:** Non utilisé
- **Network zones:** Firewalld zone "external" pour ppp0
- **MTU:** 1492 sur ppp0 (PPPoE standard)
- **Failover:** Pas de connexion backup configurée
