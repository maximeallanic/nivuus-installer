# Configuration Firewall (nftables) - Nivuus

Le système utilise nftables comme firewall principal avec plusieurs tables et règles spécialisées.

## Vue d'ensemble

- **Système de firewall:** nftables + firewalld
- **Fail2ban:** Actif (nftables backend)
- **IPv4:** Configuré
- **IPv6:** Configuré (limité)

## Tables nftables

### 1. Table f2b-table (Fail2ban)

```nftables
table inet f2b-table {
    set addr-set-sshd {
        type ipv4_addr
        flags interval
        elements = { 87.100.222.40, 222.100.181.78 }
    }

    chain f2b-chain {
        type filter hook input priority filter - 1; policy accept;
        tcp dport 22 ip saddr @addr-set-sshd reject with icmp port-unreachable
    }
}
```

**Description:**
- Fail2ban bloque automatiquement les IPs suspectes sur SSH (port 22)
- IPs actuellement bloquées: 87.100.222.40, 222.100.181.78
- Rejet avec ICMP port-unreachable

### 2. Table ip nat

```nftables
table ip nat {
    chain POSTROUTING {
        type nat hook postrouting priority srcnat; policy accept;
        tcp flags syn / syn,rst counter packets 34372 bytes 2060983 tcp option maxseg size set rt mtu
    }
}
```

**Description:**
- **MSS Clamping:** Ajuste automatiquement le MSS TCP pour PPPoE
- Essentiel pour éviter la fragmentation avec MTU 1492
- Stats: 34372 packets, ~2MB traités

### 3. Table ip mangle

```nftables
table ip mangle {
    chain FORWARD {
        type filter hook forward priority mangle; policy accept;
        tcp flags syn / fin,syn,rst,ack counter packets 4216 bytes 250805 tcp option maxseg size set rt mtu
    }

    chain PREROUTING {
        type filter hook prerouting priority mangle; policy accept;
        ct state invalid counter packets 1868 bytes 179156 drop
        tcp flags != syn / fin,syn,rst,ack ct state new counter packets 358 bytes 39754 drop
    }
}
```

**Description:**
- **FORWARD:** MSS clamping supplémentaire
- **PREROUTING:**
  - Drop packets avec état de connexion invalide (1868 packets)
  - Drop nouvelles connexions TCP sans flag SYN (358 packets)
  - Protection contre scans et attaques basiques

### 4. Table ip filter

```nftables
table ip filter {
    chain FORWARD {
        type filter hook forward priority filter; policy accept;
        iifname "ppp0" ct status dnat counter packets 8923166 bytes 12205430514 accept
        iifname "ppp0" meta l4proto icmp ct state new counter packets 0 bytes 0 accept
        iifname "ppp0" ct state invalid counter packets 0 bytes 0 drop
    }
}
```

**Description:**
- **FORWARD depuis ppp0:**
  - Accept connexions DNAT (port forwarding): 8.9M packets, 12GB
  - Accept nouvelles connexions ICMP (ping)
  - Drop packets invalides

### 5. Tables IPv6

```nftables
table ip6 nat {
    chain POSTROUTING { ... }
    chain DOCKER { }
    chain PREROUTING { jump DOCKER }
    chain OUTPUT { jump DOCKER }
}

table ip6 mangle {
    chain FORWARD { ... }
}

table ip6 filter {
    chain FORWARD {
        type filter hook forward priority filter; policy accept;
        counter packets 0 bytes 0 jump DOCKER-USER
        counter packets 0 bytes 0 jump DOCKER-FORWARD
        iifname "ppp0" ct status dnat counter packets 0 bytes 0 accept
        iifname "ppp0" meta l4proto ipv6-icmp ct state new counter packets 0 bytes 0 accept
        iifname "ppp0" ct state invalid counter packets 0 bytes 0 drop
    }
    chain DOCKER { }
    chain DOCKER-FORWARD { jump DOCKER-CT; jump DOCKER-ISOLATION-STAGE-1; jump DOCKER-BRIDGE }
    chain DOCKER-USER { }
    # ... autres chaînes Docker
}
```

**Description:**
- Règles IPv6 similaires à IPv4
- Intégration avec Docker
- 0 packets traités (IPv6 non utilisé actuellement)

### 6. Table inet firewalld

```nftables
table inet firewalld {
    ct helper helper-netbios-ns-udp {
        type "netbios-ns" protocol udp
    }
    # ... autres règles firewalld
}
```

**Description:**
- Configuration firewalld (service systemd)
- Helpers de connexion (NetBIOS, etc.)

## NAT et Port Forwarding

### TCPMSS Clamping (iptables legacy)

```bash
Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination
TCPMSS     tcp  --  0.0.0.0/0            0.0.0.0/0            tcp flags:0x06/0x02 TCPMSS clamp to PMTU
```

**Stats:** 34383 packets, 2062 KB

**Description:**
- Clamp MSS à PMTU (Path MTU) pour PPPoE
- Résout les problèmes de MTU avec connexions PPPoE (MTU 1492)
- Critique pour éviter black holes et fragmentation

### Port Forwarding

Pas de règles DNAT explicites visibles, mais stats montrent:
- 8.9M packets DNAT acceptés (12GB de données)
- Probablement configuré via firewalld ou règles dynamiques

## Politique de Sécurité

### Politiques par Défaut

| Chaîne | Table | Politique |
|--------|-------|-----------|
| INPUT | filter | ACCEPT ⚠️ |
| FORWARD | filter | ACCEPT ⚠️ |
| OUTPUT | filter | ACCEPT |
| POSTROUTING | nat | ACCEPT |
| PREROUTING | mangle | ACCEPT |

⚠️ **Note de sécurité:** Politiques ACCEPT par défaut - Sécurité assurée par règles explicites

### Protections Actives

✅ **Fail2ban SSH** - Bloque IPs suspectes automatiquement
✅ **Drop packets invalides** - Protection état de connexion
✅ **Drop nouvelles connexions sans SYN** - Anti-scan TCP
✅ **MSS Clamping** - Optimisation PPPoE
✅ **Firewalld zones** - Séparation zones réseau

### Zones Firewalld

- **external:** ppp0 (Internet)
- **internal:** localBridge, publicBridge
- **trusted:** internalBridge (VMs)

## Configuration Fail2ban

### Service SSH

```bash
# Jails actifs
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
```

**IPs actuellement bannies:**
- 87.100.222.40
- 222.100.181.78

### Commandes Fail2ban

```bash
# Statut global
sudo fail2ban-client status

# Statut jail SSH
sudo fail2ban-client status sshd

# Débannir une IP
sudo fail2ban-client set sshd unbanip 87.100.222.40

# Voir les bans
sudo nft list set inet f2b-table addr-set-sshd
```

## Règles de Filtrage Détaillées

### Traffic Entrant (INPUT)

1. **Fail2ban** (priorité filter-1)
   - Bloque IPs SSH bannies
   - Reject avec ICMP port-unreachable

2. **Connexions établies** (conntrack)
   - Accept RELATED,ESTABLISHED automatiquement

3. **Services exposés:**
   - SSH (22) - protégé par fail2ban
   - HTTP (80) - redirect HTTPS
   - HTTPS (443, 5443) - Envoy reverse proxy
   - Autres (voir system-audit.md)

### Traffic Sortant (OUTPUT)

- Policy ACCEPT (pas de restrictions)
- Connexions sortantes libres

### Traffic Transféré (FORWARD)

1. **Depuis Internet (ppp0):**
   - Accept DNAT (port forwarding)
   - Accept ICMP (ping)
   - Drop invalides

2. **Vers Internet:**
   - Masquerading NAT automatique
   - MSS clamping actif

3. **Inter-bridges:**
   - Traffic libre entre bridges internes
   - Docker gère isolation conteneurs

## Statistiques

### Compteurs nftables

```
Packets invalides droppés:     1868 packets (179 KB)
Nouvelles connexions sans SYN:  358 packets (39 KB)
DNAT acceptés:                  8.9M packets (12 GB)
MSS clamping (NAT):            34383 packets (2 MB)
MSS clamping (FORWARD):         4216 packets (250 KB)
```

## Monitoring

### Voir les règles actives

```bash
# Toutes les tables nftables
sudo nft list ruleset

# Table spécifique
sudo nft list table inet f2b-table
sudo nft list table ip nat
sudo nft list table ip filter

# Avec compteurs
sudo nft -s list ruleset
```

### Logs Firewall

```bash
# Logs fail2ban
sudo journalctl -u fail2ban -f

# Logs firewalld
sudo journalctl -u firewalld -f

# Logs kernel (netfilter)
sudo dmesg -T | grep -i "nf_"
```

### Traffic Analysis

```bash
# Voir connexions actives
sudo conntrack -L

# Statistiques conntrack
sudo conntrack -S

# Top connexions
sudo iftop -i ppp0
```

## Optimisations PPPoE

### MSS Clamping

**Problème:** MTU PPPoE = 1492, MTU Ethernet standard = 1500
**Solution:** MSS clamping automatique

```
TCP MSS = MTU - IP header (20) - TCP header (20)
MSS clamping = 1452 (pour MTU 1492)
```

**Configuration active:**
- POSTROUTING NAT: Clamp MSS to PMTU
- FORWARD MANGLE: Clamp MSS to PMTU

**Résultat:**
- Pas de fragmentation
- Pas de black holes
- Performance optimale

## Recommandations Sécurité

### Court Terme

1. ⚠️ **Durcir politique par défaut**
   ```bash
   # Changer INPUT policy à DROP
   nft add rule ip filter INPUT policy drop
   # Puis ajouter règles explicites
   ```

2. ✅ **Activer logging sélectif**
   ```bash
   nft add rule ip filter INPUT ct state invalid counter log prefix "DROP invalid: " drop
   ```

3. ✅ **Rate limiting**
   ```bash
   nft add rule ip filter INPUT tcp dport 22 ct state new limit rate 10/minute accept
   ```

### Long Terme

1. **Géolocalisation:** Bloquer pays non nécessaires
2. **DDoS protection:** Rate limiting par IP
3. **IDS/IPS:** Crowdsec déjà actif - étendre à plus de services
4. **IPv6:** Configurer si nécessaire
5. **Backup config:** Sauvegarder règles régulièrement

## Sauvegarde et Restauration

### Sauvegarder configuration

```bash
# nftables
sudo nft list ruleset > /etc/nftables.conf

# Fail2ban
sudo fail2ban-client get sshd banip > /etc/fail2ban/banned-ips.txt

# Firewalld
sudo firewall-cmd --runtime-to-permanent
```

### Restaurer configuration

```bash
# nftables
sudo nft -f /etc/nftables.conf

# Fail2ban (se restaure automatiquement)
sudo systemctl restart fail2ban
```

## Troubleshooting

### Connexion bloquée

```bash
# Vérifier si IP est bannie
sudo nft list set inet f2b-table addr-set-sshd

# Débannir
sudo fail2ban-client set sshd unbanip <IP>
```

### Port forwarding ne fonctionne pas

```bash
# Vérifier NAT
sudo nft list table ip nat

# Vérifier FORWARD
sudo nft list chain ip filter FORWARD

# Vérifier conntrack
sudo conntrack -L | grep <port>
```

### MTU/MSS issues

```bash
# Tester MTU
ping -M do -s 1472 8.8.8.8  # 1472 + 28 = 1500
ping -M do -s 1464 8.8.8.8  # 1464 + 28 = 1492 (PPPoE)

# Vérifier MSS clamping
sudo tcpdump -i ppp0 -vvv 'tcp[tcpflags] & tcp-syn != 0'
```

---

**Dernière mise à jour:** 2025-10-18
**Version nftables:** (voir `nft --version`)
**Version firewalld:** (voir `firewall-cmd --version`)
