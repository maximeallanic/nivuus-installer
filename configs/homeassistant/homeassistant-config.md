# Configuration Home Assistant - Nivuus

Home Assistant est le système de domotique central du serveur Nivuus, gérant l'automatisation, le monitoring et le contrôle des appareils.

## Vue d'ensemble

- **Conteneur:** homeassistant
- **Image:** ghcr.io/home-assistant/home-assistant:stable
- **Network Mode:** host
- **Port:** 8123 (HTTP)
- **Config:** /opt/nivuus/HomeAssistant/config

## Configuration Réseau

### Network Mode: Host

```yaml
network_mode: host
```

**Avantages:**
- Accès direct à toutes les interfaces réseau
- Découverte automatique appareils (mDNS/UPnP)
- Performance optimale
- Émulation Hue sur port 80

**Inconvénients:**
- Pas d'isolation réseau Docker
- Partage stack réseau avec l'hôte

### Ports Exposés

| Port | Service | Description |
|------|---------|-------------|
| **8123** | HTTP/WebSocket | Interface web Home Assistant |
| **80** | HTTP | Emulated Hue (contrôle Alexa/Google) |
| **5353** | mDNS | Découverte automatique |
| **1900** | SSDP/UPnP | Découverte appareils |

### Adresse d'Accès

- **Local:** http://192.168.0.1:8123
- **Externe:** Accessible via Pomerium reverse proxy

## Configuration Principale

**Fichier:** `/opt/nivuus/HomeAssistant/config/configuration.yaml`

### Logging

```yaml
logger:
  default: warning
```

Niveau de log minimal pour réduire verbosité.

### Default Config

```yaml
default_config:
```

Active les intégrations par défaut:
- Frontend
- History
- Logbook
- Map
- Mobile app
- Person
- Sun
- System Health
- Etc.

### Organisation

```yaml
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
mqtt: !include server.yml
```

Configuration modulaire avec fichiers séparés.

## MQTT Configuration

**Fichier:** `/opt/nivuus/HomeAssistant/config/server.yml`

```yaml
mqtt: !include server.yml
```

**Broker MQTT:**
- Conteneur: mosquitto
- Ports: 1883 (standard), 1884 (WebSocket), 8883 (TLS), 8884 (TLS WS)
- Protocole: MQTT 3.1/3.1.1/5.0

**Utilisation:**
- Appareils IoT (DIYHue, Zigbee, etc.)
- Échange messages entre services
- Automation triggers

## Emulated Hue

```yaml
emulated_hue:
  listen_port: 80
  host_ip: 192.168.0.1
```

**Fonction:**
- Émule un Philips Hue Bridge
- Permet contrôle via Alexa/Google Assistant
- Expose entités Home Assistant comme lumières Hue

**Exposition:**
- Port 80 (HTTP)
- IP: 192.168.0.1 (localBridge)
- Découvrable via SSDP

## Authentication

### Providers

```yaml
homeassistant:
  auth_providers:
    - type: homeassistant
    - type: trusted_networks
      trusted_networks:
        - 192.168.0.0/24
        - 127.0.0.1
      allow_bypass_login: true
```

**Méthodes d'authentification:**

1. **homeassistant** - Login/password standard
2. **trusted_networks** - Auto-login depuis réseaux fiables
   - 192.168.0.0/24 (localBridge)
   - 127.0.0.1 (localhost)

**allow_bypass_login:** Pas de prompt login sur trusted networks

### MFA (Multi-Factor Authentication)

```yaml
  auth_mfa_modules:
    - type: totp
      name: Authenticator app
```

Support TOTP (Time-based One-Time Password) via apps:
- Google Authenticator
- Authy
- Microsoft Authenticator

### Zones

```yaml
  customize:
    zone.home:
      radius: 30
```

Zone "home" avec rayon de 30 mètres pour présence/géofencing.

## HTTP Configuration

```yaml
http:
  use_x_forwarded_for: true
  use_x_frame_options: false
  trusted_proxies:
    - 192.168.0.1
    - 127.0.0.1
    - ::1
```

**use_x_forwarded_for:**
- Récupère vraie IP client via reverse proxy (Pomerium/Envoy)
- Important pour logging et sécurité

**use_x_frame_options:**
- Désactive X-Frame-Options
- Permet iframe (ex: dans dashboards externes)

**trusted_proxies:**
- IPs autorisées à forwarder requêtes
- Nécessaire pour X-Forwarded-For

## Recorder (Base de Données)

```yaml
recorder:
  purge_keep_days: 5
```

**Fonction:**
- Enregistre historique entités
- Base de données SQLite par défaut
- Purge automatique après 5 jours

**Performance:**
- Limite croissance DB
- Réduit overhead I/O
- Optimise queries

## Docker Monitoring

```yaml
monitor_docker:
  - name: Docker
    url: unix://var/run/docker.sock
    containers:
      - mediamanager-tdarr-node-1
      - mediamanager-tdarr-1
      - languagetool
      - postgres
      - mediamanager-bazarr-4k-1
      - mediamanager-bazarr-1
      - mediamanager-prowlarr-1
      - mediamanager-radarr-1
      - mediamanager-radarr-4k-1
      - mediamanager-aria2-1
      - mediamanager-gluetun-1
      - mediamanager-sonarr-1
      - mediamanager-sonarr-4k-1
      - mediamanager-openai-whisper-asr-webservice-1
      - allanicme-frontend-1
      - mediamanager-overseerr-1
      - mediamanager-flaresolverr-1
      - guacamole-web-1
      - gcpdynamicdns-dyndns-1
```

**Intégration:** monitor_docker (HACS)

**Métriques surveillées:**
```yaml
    monitored_conditions:
      - version
      - containers_running
      - containers_total
      - state
      - status
      - memory
```

**Affichage:**
- État conteneurs
- Consommation mémoire
- Uptime
- Redémarrages

**Accès Docker socket:**
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

## Google Assistant Integration

```yaml
google_assistant:
  project_id: allanic-me-357213
```

**Fonction:**
- Contrôle vocal via Google Assistant
- Exposition entités sélectionnées
- Actions vocales personnalisées

**Configuration GCP:**
- Project ID: allanic-me-357213
- Actions on Google
- OAuth2 authentication

## Volumes et Montages

### Configuration Directory

**Host:** `/opt/nivuus/HomeAssistant/config`
**Container:** `/config`

**Contenu:**
```
/opt/nivuus/HomeAssistant/config/
├── configuration.yaml      # Config principale
├── automations.yaml        # Automations
├── scripts.yaml            # Scripts
├── scenes.yaml             # Scènes
├── server.yml              # MQTT config
├── .storage/               # DB interne (JSON)
├── custom_components/      # Intégrations custom
├── www/                    # Fichiers statiques
├── themes/                 # Thèmes UI
├── blueprints/             # Automation blueprints
├── backups/                # Backups auto
├── appdaemon/              # AppDaemon config
├── diyhue/                 # DIYHue integration
└── peugeot208/             # PSA Car Controller
```

### Autres Montages

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
  - /dev:/dev:rw
  - /etc/localtime:/etc/localtime:ro
```

**docker.sock:** Monitoring conteneurs
**/dev:** Accès devices (USB, serial, etc.)
**/etc/localtime:** Timezone sync

## Intégrations Principales

### Custom Components

**Répertoire:** `/opt/nivuus/HomeAssistant/config/custom_components/`

Intégrations personnalisées installées (probablement via HACS):
- monitor_docker
- PSA Car Controller (Peugeot 208)
- Autres intégrations custom

### Services Intégrés

**DIYHue:**
- Conteneur: diyhue
- Émulation Philips Hue
- Contrôle lumières locales

**MQTT (Mosquitto):**
- Broker central
- Communication IoT

**Docker Monitoring:**
- 22+ conteneurs surveillés
- Métriques temps réel

### Appareils Connectés

D'après la configuration:
- **Peugeot 208** (PSA Car Controller)
- **Appareils Philips Hue** (via DIYHue)
- **Appareils MQTT** (Zigbee, etc.)
- **Serveur Plex** (monitoring)
- **Stack média** (Sonarr, Radarr, etc.)

## Automatisations

**Fichier:** `automations.yaml`

**Exemples d'automatisations possibles:**
- Contrôle éclairage automatique
- Notifications état conteneurs
- Monitoring température CPU/GPU
- Actions basées sur présence
- Intégration voiture (PSA)

## Security

### Authentification

✅ **Multi-provider** - Login + Trusted networks
✅ **MFA (TOTP)** - 2FA disponible
✅ **Trusted proxies** - Liste restreinte

### Réseau

✅ **Reverse proxy** - Pomerium pour accès externe
✅ **Trusted networks** - 192.168.0.0/24 only
⚠️ **Network: host** - Pas d'isolation Docker

### Recommandations

1. **Activer MFA** pour tous les comptes admin
2. **Limiter trusted_networks** si besoin
3. **HTTPS** via reverse proxy obligatoire
4. **API tokens** - Gérer avec précaution
5. **Backups réguliers** du dossier .storage/

## Backup et Restauration

### Backup Automatique

Home Assistant crée des backups dans:
```
/opt/nivuus/HomeAssistant/config/backups/
```

### Backup Manuel

```bash
# Backup config complet
sudo tar czf /backup/homeassistant-$(date +%Y%m%d).tar.gz \
  /opt/nivuus/HomeAssistant/config/

# Backup sélectif (sans cache)
sudo tar czf /backup/homeassistant-config-$(date +%Y%m%d).tar.gz \
  --exclude='*.db' \
  --exclude='*.log' \
  --exclude='.cloud' \
  --exclude='deps' \
  /opt/nivuus/HomeAssistant/config/
```

### Restauration

```bash
# Arrêter conteneur
docker stop homeassistant

# Restaurer
sudo tar xzf /backup/homeassistant-20251018.tar.gz -C /

# Redémarrer
docker start homeassistant
```

## Monitoring et Logs

### Logs Conteneur

```bash
# Logs temps réel
docker logs -f homeassistant

# Dernières 100 lignes
docker logs --tail 100 homeassistant

# Logs avec timestamps
docker logs -t homeassistant
```

### Logs Home Assistant

**Via UI:**
- Configuration → Logs
- Niveau de log configurable

**Via fichier:**
```bash
tail -f /opt/nivuus/HomeAssistant/config/home-assistant.log
```

### Métriques

**Intégration System Monitor:**
- CPU usage (host)
- Memory usage
- Disk usage
- Network stats

**Intégration Docker Monitor:**
- État conteneurs
- Ressources utilisées
- Redémarrages

## Commandes Utiles

### Gestion Conteneur

```bash
# Status
docker ps | grep homeassistant

# Redémarrer
docker restart homeassistant

# Shell dans conteneur
docker exec -it homeassistant bash

# Vérifier config
docker exec homeassistant python -m homeassistant --script check_config -c /config
```

### CLI Home Assistant

```bash
# Accès CLI
docker exec -it homeassistant bash

# Dans le conteneur:
ha core restart
ha core check
ha supervisor info
ha dns info
```

### API REST

```bash
# Token API requis
TOKEN="your-long-lived-access-token"

# État entité
curl -H "Authorization: Bearer $TOKEN" \
  http://192.168.0.1:8123/api/states/sensor.cpu_temp

# Liste entités
curl -H "Authorization: Bearer $TOKEN" \
  http://192.168.0.1:8123/api/states

# Appeler service
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.bedroom"}' \
  http://192.168.0.1:8123/api/services/light/turn_on
```

## Intégrations Recommandées

### Monitoring Serveur

- **System Monitor** - CPU, RAM, Disk
- **Speedtest** - Vitesse Internet
- **Uptime** - Disponibilité services

### Automations

- **Node-RED** - Automations visuelles
- **AppDaemon** - Automations Python

### UI/UX

- **Lovelace UI** - Dashboards personnalisés
- **Themes** - Personnalisation visuelle
- **Custom Cards** (HACS)

### Notifications

- **Mobile App** - Notifications push
- **Telegram** - Bot notifications
- **Email** - Alertes critiques

## Troubleshooting

### Home Assistant ne démarre pas

```bash
# Vérifier logs
docker logs homeassistant

# Vérifier config
docker exec homeassistant python -m homeassistant --script check_config -c /config

# Permissions
sudo chown -R root:root /opt/nivuus/HomeAssistant/config/
```

### Émulation Hue ne fonctionne pas

```bash
# Vérifier port 80
sudo ss -tlnp | grep :80

# Tester discovery
sudo tcpdump -i localBridge port 1900

# Logs Hue
docker logs homeassistant | grep emulated_hue
```

### Docker monitoring absent

```bash
# Vérifier socket montage
docker inspect homeassistant | grep docker.sock

# Permissions socket
sudo chmod 666 /var/run/docker.sock  # Temporaire, insécure

# Vérifier intégration
# Configuration → Intégrations → Monitor Docker
```

### Performances lentes

```bash
# Vérifier taille DB
du -h /opt/nivuus/HomeAssistant/config/home-assistant_v2.db

# Purger historique
# Configuration → Système → Base de données

# Optimiser recorder
# Limiter purge_keep_days
# Exclure entités fréquentes
```

## Dashboards et UI

### Lovelace

**Configuration:**
- UI Mode: Storage (stocké dans .storage/)
- Édition visuelle activée

**Dashboards:**
- Overview (par défaut)
- Custom dashboards

### Thèmes

**Répertoire:** `/opt/nivuus/HomeAssistant/config/themes/`

**Application:**
```yaml
# Dans configuration.yaml
frontend:
  themes: !include_dir_merge_named themes/
```

## Performance

### Optimisations Actuelles

✅ **Purge DB: 5 jours** - Limite croissance
✅ **Logger: warning** - Réduit I/O
✅ **Network: host** - Performance réseau

### Optimisations Recommandées

1. **PostgreSQL** - Migration depuis SQLite
   ```yaml
   recorder:
     db_url: postgresql://user:pass@localhost/homeassistant
   ```

2. **Exclure entités fréquentes**
   ```yaml
   recorder:
     exclude:
       entities:
         - sensor.time
         - sensor.date
   ```

3. **Commit interval**
   ```yaml
   recorder:
     commit_interval: 30  # Secondes
   ```

## Sécurité Avancée

### Secrets Management

```yaml
# secrets.yaml
http_password: !secret http_password
mqtt_password: !secret mqtt_password
```

**Fichier:** `/opt/nivuus/HomeAssistant/config/secrets.yaml`

### API Security

- **Long-lived tokens** - Pour intégrations
- **Webhook IDs** - Aléatoires et uniques
- **Trusted proxies** - Liste restreinte

### Network Security

- **Firewall** - Zone "home" configurée
- **Reverse proxy** - Pomerium avec auth
- **Trusted networks** - Whitelist IP

---

**Dernière mise à jour:** 2025-10-18
**Version Home Assistant:** Stable (voir container)
**Config Path:** /opt/nivuus/HomeAssistant/config
