# Home Assistant CLI - Nivuus

Guide d'installation et utilisation du CLI Home Assistant pour interagir avec l'API REST depuis la ligne de commande Linux.

## Vue d'ensemble

**ha** est un wrapper CLI qui permet d'interagir avec Home Assistant directement depuis le terminal. C'est utile pour:
- Automatisation via scripts bash
- Tests et debugging rapides
- Intégration avec d'autres outils système
- Monitoring et contrôle depuis SSH
- Déclenchement d'actions depuis des hooks système

## Architecture

```
Linux Host                    Home Assistant
┌─────────────┐              ┌──────────────┐
│             │  HTTP/HTTPS  │              │
│   ha CLI    │─────────────>│  REST API    │
│  wrapper    │  Port 8123   │              │
│             │              │              │
└─────────────┘              └──────────────┘
      │                             │
      v                             v
    curl                         API
   (HTTP)                     Endpoints
```

## Installation

### Étape 1: Installer le CLI

```bash
cd /home/mallanic/Projects/Nivuus
sudo install -m 755 scripts/ha /usr/local/bin/ha
```

**Vérification:**
```bash
ha --help
# Doit afficher l'aide
```

### Étape 2: Installer jq (optionnel mais recommandé)

Pour un formatage JSON plus lisible:

```bash
sudo apt-get install jq
```

### Étape 3: Créer un Long-Lived Access Token

Dans Home Assistant:

1. Ouvrir l'interface web Home Assistant
2. Cliquer sur votre profil (icône en bas à gauche)
3. Scroller jusqu'à "Long-Lived Access Tokens"
4. Cliquer "Create Token"
5. Donner un nom (ex: "Nivuus CLI")
6. Copier le token généré (vous ne pourrez plus le voir après!)

### Étape 4: Configurer les credentials

```bash
# Créer le répertoire de configuration
mkdir -p ~/.config/nivuus

# Créer le fichier de configuration
cat > ~/.config/nivuus/ha.conf << 'EOF'
HA_URL="http://192.168.1.100:8123"
HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-long-token-here"
EOF

# Sécuriser le fichier (important!)
chmod 600 ~/.config/nivuus/ha.conf
```

**Variables:**
- `HA_URL`: URL de votre instance Home Assistant (avec port)
- `HA_TOKEN`: Long-lived access token créé à l'étape 3

**Exemples d'URLs:**
```bash
# IP locale
HA_URL="http://192.168.1.100:8123"

# Hostname mDNS
HA_URL="http://homeassistant.local:8123"

# HTTPS avec certificat
HA_URL="https://ha.example.com:8123"

# Nabu Casa (cloud)
HA_URL="https://xxxxx.ui.nabu.casa"
```

## Vérification

### Test basique

```bash
# Obtenir la configuration Home Assistant
ha config

# Lister toutes les entités
ha states

# Obtenir l'état d'une entité spécifique
ha states light.living_room
```

### Troubleshooting

#### Erreur: "Failed to connect to Home Assistant"

**Cause:** URL incorrecte ou Home Assistant inaccessible.

**Solution:**
```bash
# Vérifier que Home Assistant est accessible
curl -I http://192.168.1.100:8123

# Vérifier la configuration
cat ~/.config/nivuus/ha.conf

# Tester avec l'URL directement
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://192.168.1.100:8123/api/
```

#### Erreur: "401 Unauthorized"

**Cause:** Token invalide ou expiré.

**Solution:**
1. Créer un nouveau long-lived token dans Home Assistant
2. Mettre à jour le fichier de configuration
3. Vérifier que le token est correctement copié (pas d'espaces)

#### Erreur: "404 Not Found"

**Cause:** Entité ou service inexistant.

**Solution:**
```bash
# Lister toutes les entités disponibles
ha states | grep "entity_id"

# Vérifier les services disponibles dans HA
ha raw /api/services
```

#### JSON non formaté

**Cause:** jq n'est pas installé.

**Solution:**
```bash
sudo apt-get install jq
```

## Commandes

### states - États des entités

Lire les états des entités Home Assistant.

```bash
# Lister toutes les entités et leurs états
ha states

# État d'une entité spécifique
ha states light.living_room
ha states sensor.temperature
ha states switch.coffee_maker

# Filtrer avec jq (si installé)
ha states | jq '.[] | select(.entity_id | startswith("light."))'
ha states | jq '.[] | select(.state == "on")'
```

**Exemples de réponses:**

```json
{
  "entity_id": "light.living_room",
  "state": "on",
  "attributes": {
    "brightness": 255,
    "color_temp": 370,
    "friendly_name": "Living Room Light"
  },
  "last_changed": "2025-01-15T10:30:00.000000+00:00",
  "last_updated": "2025-01-15T10:30:00.000000+00:00"
}
```

### service - Appeler des services

Exécuter des services Home Assistant pour contrôler les entités.

**Syntaxe:**
```bash
ha service <domain> <service> '<json_data>'
```

**Exemples:**

```bash
# Allumer une lumière
ha service light turn_on '{"entity_id": "light.living_room"}'

# Allumer avec luminosité
ha service light turn_on '{"entity_id": "light.bedroom", "brightness_pct": 50}'

# Allumer avec couleur RGB
ha service light turn_on '{"entity_id": "light.rgb", "rgb_color": [255, 0, 0]}'

# Éteindre
ha service light turn_off '{"entity_id": "light.kitchen"}'

# Allumer toutes les lumières
ha service light turn_on '{"entity_id": "all"}'

# Switch toggle
ha service switch toggle '{"entity_id": "switch.fan"}'

# Média player
ha service media_player media_play '{"entity_id": "media_player.living_room"}'
ha service media_player volume_set '{"entity_id": "media_player.bedroom", "volume_level": 0.5}'

# Thermostat
ha service climate set_temperature '{"entity_id": "climate.bedroom", "temperature": 22}'

# Déclencher une automation
ha service automation trigger '{"entity_id": "automation.morning_routine"}'

# Exécuter un script
ha service script turn_on '{"entity_id": "script.movie_time"}'

# Notification
ha service notify.mobile_app '{"message": "Hello from CLI!"}'
ha service notify.persistent_notification '{"message": "Task done", "title": "Info"}'
```

### config - Configuration

Obtenir la configuration de Home Assistant.

```bash
ha config
```

**Réponse:**
```json
{
  "latitude": 48.8566,
  "longitude": 2.3522,
  "elevation": 0,
  "unit_system": {
    "length": "km",
    "mass": "g",
    "temperature": "°C",
    "volume": "L"
  },
  "location_name": "Home",
  "time_zone": "Europe/Paris",
  "version": "2025.1.0"
}
```

### events - Déclencher des événements

Envoyer des événements personnalisés.

```bash
# Événement simple
ha events test_event

# Événement avec données
ha events custom_event '{"message": "Hello", "source": "cli"}'

# Événement automation
ha events automation_triggered '{"entity_id": "automation.test"}'
```

### template - Évaluer des templates

Évaluer des templates Jinja2.

```bash
# Lire une valeur de capteur
ha template '{{ states("sensor.temperature") }}'

# Lire un attribut
ha template '{{ state_attr("light.living_room", "brightness") }}'

# Calculs
ha template '{{ states("sensor.temperature") | float + 10 }}'

# Conditions
ha template '{% if is_state("light.bedroom", "on") %}ON{% else %}OFF{% endif %}'
```

### raw - Appels API directs

Faire des appels API personnalisés.

```bash
# GET simple
ha raw /api/

# GET avec endpoint
ha raw /api/services
ha raw /api/events
ha raw /api/error_log

# POST avec données
ha raw /api/services/light/turn_on POST '{"entity_id": "light.kitchen"}'

# Découverte
ha raw /api/discovery_info
```

## Usage Avancé

### Scripts d'automatisation

**Exemple 1: Monitoring de température**

```bash
#!/bin/bash
# monitor-temp.sh - Surveiller la température et alerter

TEMP=$(ha template '{{ states("sensor.temperature") | float }}')
THRESHOLD=25

if (( $(echo "$TEMP > $THRESHOLD" | bc -l) )); then
    ha service notify.persistent_notification \
        "{\"message\": \"Temperature: ${TEMP}°C\", \"title\": \"Alert\"}"

    # Allumer le ventilateur
    ha service switch turn_on '{"entity_id": "switch.fan"}'
fi
```

**Exemple 2: Routine du matin**

```bash
#!/bin/bash
# morning-routine.sh - Routine matinale

# Allumer les lumières progressivement
ha service light turn_on '{"entity_id": "light.bedroom", "brightness_pct": 10}'
sleep 30
ha service light turn_on '{"entity_id": "light.bedroom", "brightness_pct": 50}'
sleep 30
ha service light turn_on '{"entity_id": "light.bedroom", "brightness_pct": 100}'

# Démarrer la cafetière
ha service switch turn_on '{"entity_id": "switch.coffee_maker"}'

# Notification
ha service notify.mobile_app '{"message": "Good morning! Coffee is ready."}'
```

**Exemple 3: Sauvegarde des états**

```bash
#!/bin/bash
# backup-states.sh - Sauvegarder l'état de toutes les entités

BACKUP_DIR="$HOME/ha-backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ha states > "$BACKUP_DIR/states_${TIMESTAMP}.json"

echo "Backup saved: states_${TIMESTAMP}.json"
```

**Exemple 4: Toggle basé sur l'heure**

```bash
#!/bin/bash
# auto-lights.sh - Allumer/éteindre selon l'heure

HOUR=$(date +%H)

if [[ $HOUR -ge 18 ]] || [[ $HOUR -lt 7 ]]; then
    # Nuit: allumer les lumières
    ha service light turn_on '{"entity_id": "light.outdoor"}'
else
    # Jour: éteindre les lumières
    ha service light turn_off '{"entity_id": "light.outdoor"}'
fi
```

### Intégration avec Cron

```bash
# Éditer crontab
crontab -e

# Ajouter des tâches automatiques
# Routine du matin à 7h00
0 7 * * * /home/mallanic/scripts/morning-routine.sh

# Lumières extérieures au coucher du soleil
0 18 * * * /usr/local/bin/ha service light turn_on '{"entity_id": "light.outdoor"}'

# Monitoring température toutes les 5 minutes
*/5 * * * * /home/mallanic/scripts/monitor-temp.sh

# Sauvegarde quotidienne à minuit
0 0 * * * /home/mallanic/scripts/backup-states.sh
```

### Variables d'environnement

Alternative au fichier config:

```bash
export HA_URL="http://192.168.1.100:8123"
export HA_TOKEN="your-token-here"

ha states
```

### Parsing avec jq

```bash
# Lister uniquement les entity_ids
ha states | jq -r '.[].entity_id'

# Lumières allumées
ha states | jq -r '.[] | select(.entity_id | startswith("light.")) | select(.state == "on") | .entity_id'

# Température de tous les capteurs
ha states | jq -r '.[] | select(.entity_id | startswith("sensor.")) | select(.attributes.unit_of_measurement == "°C") | "\(.entity_id): \(.state)°C"'

# Luminosité moyenne
ha states | jq '[.[] | select(.entity_id | startswith("light.")) | select(.state == "on") | .attributes.brightness] | add / length'

# Entités avec batterie faible
ha states | jq -r '.[] | select(.attributes.battery_level != null) | select(.attributes.battery_level < 20) | "\(.entity_id): \(.attributes.battery_level)%"'
```

### Boucles et monitoring

```bash
# Monitoring en continu
while true; do
    clear
    echo "=== Home Assistant Status ==="
    echo "Time: $(date)"
    echo ""

    # Température
    TEMP=$(ha template '{{ states("sensor.temperature") }}')
    echo "Temperature: ${TEMP}°C"

    # Lumières allumées
    LIGHTS_ON=$(ha states | jq '[.[] | select(.entity_id | startswith("light.")) | select(.state == "on")] | length')
    echo "Lights on: ${LIGHTS_ON}"

    # Consommation électrique (si disponible)
    POWER=$(ha template '{{ states("sensor.power_consumption") }}' 2>/dev/null || echo "N/A")
    echo "Power: ${POWER}W"

    sleep 5
done
```

## Exemples par domaine

### Lumières (light)

```bash
# On/Off
ha service light turn_on '{"entity_id": "light.bedroom"}'
ha service light turn_off '{"entity_id": "light.bedroom"}'
ha service light toggle '{"entity_id": "light.bedroom"}'

# Luminosité (0-255 ou percentage)
ha service light turn_on '{"entity_id": "light.desk", "brightness": 128}'
ha service light turn_on '{"entity_id": "light.desk", "brightness_pct": 50}'

# Couleur RGB (0-255 pour chaque canal)
ha service light turn_on '{"entity_id": "light.rgb", "rgb_color": [255, 0, 0]}'  # Rouge
ha service light turn_on '{"entity_id": "light.rgb", "rgb_color": [0, 255, 0]}'  # Vert
ha service light turn_on '{"entity_id": "light.rgb", "rgb_color": [0, 0, 255]}'  # Bleu

# Température de couleur (mireds)
ha service light turn_on '{"entity_id": "light.white", "color_temp": 370}'  # Chaud
ha service light turn_on '{"entity_id": "light.white", "color_temp": 154}'  # Froid

# Transition (en secondes)
ha service light turn_on '{"entity_id": "light.bedroom", "brightness_pct": 100, "transition": 30}'

# Effet
ha service light turn_on '{"entity_id": "light.strip", "effect": "colorloop"}'

# Groupes
ha service light turn_on '{"entity_id": "light.all_lights"}'
ha service light turn_off '{"entity_id": ["light.living_room", "light.kitchen", "light.bedroom"]}'
```

### Switches (switch)

```bash
# On/Off/Toggle
ha service switch turn_on '{"entity_id": "switch.coffee_maker"}'
ha service switch turn_off '{"entity_id": "switch.fan"}'
ha service switch toggle '{"entity_id": "switch.lamp"}'

# Tous les switches
ha service switch turn_off '{"entity_id": "all"}'
```

### Media Players (media_player)

```bash
# Lecture
ha service media_player media_play '{"entity_id": "media_player.living_room"}'
ha service media_player media_pause '{"entity_id": "media_player.living_room"}'
ha service media_player media_stop '{"entity_id": "media_player.living_room"}'
ha service media_player media_next_track '{"entity_id": "media_player.spotify"}'
ha service media_player media_previous_track '{"entity_id": "media_player.spotify"}'

# Volume (0.0 - 1.0)
ha service media_player volume_set '{"entity_id": "media_player.bedroom", "volume_level": 0.5}'
ha service media_player volume_up '{"entity_id": "media_player.bedroom"}'
ha service media_player volume_down '{"entity_id": "media_player.bedroom"}'
ha service media_player volume_mute '{"entity_id": "media_player.tv", "is_volume_muted": true}'

# Lecture d'URL
ha service media_player play_media '{"entity_id": "media_player.living_room", "media_content_type": "music", "media_content_id": "https://example.com/song.mp3"}'
```

### Climate (climate)

```bash
# Température
ha service climate set_temperature '{"entity_id": "climate.bedroom", "temperature": 22}'
ha service climate set_temperature '{"entity_id": "climate.living_room", "temperature": 20, "target_temp_high": 24, "target_temp_low": 18}'

# Mode HVAC
ha service climate set_hvac_mode '{"entity_id": "climate.bedroom", "hvac_mode": "heat"}'
# Modes: off, heat, cool, heat_cool, auto, dry, fan_only

# Mode preset
ha service climate set_preset_mode '{"entity_id": "climate.bedroom", "preset_mode": "away"}'
# Presets: none, eco, away, boost, comfort, home, sleep, activity

# Ventilateur
ha service climate set_fan_mode '{"entity_id": "climate.living_room", "fan_mode": "auto"}'
```

### Automations (automation)

```bash
# Déclencher
ha service automation trigger '{"entity_id": "automation.morning_routine"}'

# Activer/Désactiver
ha service automation turn_on '{"entity_id": "automation.night_mode"}'
ha service automation turn_off '{"entity_id": "automation.night_mode"}'

# Toggle
ha service automation toggle '{"entity_id": "automation.auto_lights"}'

# Recharger les automations
ha service automation reload '{}'
```

### Scripts (script)

```bash
# Exécuter
ha service script turn_on '{"entity_id": "script.movie_time"}'
ha service script.movie_time '{}'  # Forme courte

# Avec variables
ha service script.notify_mobile '{"variables": {"message": "Hello", "title": "Info"}}'

# Arrêter
ha service script turn_off '{"entity_id": "script.long_running"}'

# Recharger
ha service script reload '{}'
```

### Notifications (notify)

```bash
# Notification persistante (dans HA)
ha service notify.persistent_notification '{"message": "Task completed", "title": "Success"}'

# Mobile app
ha service notify.mobile_app_pixel '{"message": "You have a visitor!"}'
ha service notify.mobile_app_iphone '{"message": "Door opened", "title": "Alert"}'

# Avec données supplémentaires
ha service notify.mobile_app '{"message": "Check this", "data": {"clickAction": "/lovelace/cameras"}}'

# Groupe de notification
ha service notify.all_devices '{"message": "System update available"}'
```

### Covers (cover)

```bash
# Ouvrir/Fermer
ha service cover open_cover '{"entity_id": "cover.garage_door"}'
ha service cover close_cover '{"entity_id": "cover.garage_door"}'
ha service cover stop_cover '{"entity_id": "cover.garage_door"}'

# Position (0-100)
ha service cover set_cover_position '{"entity_id": "cover.blinds", "position": 50}'

# Inclinaison
ha service cover set_cover_tilt_position '{"entity_id": "cover.blinds", "tilt_position": 45}'
```

## Sécurité

### Avertissements

- Le token donne un accès COMPLET à votre Home Assistant
- Ne jamais commiter le fichier de configuration dans Git
- Protéger le fichier avec chmod 600
- Révoquer les tokens non utilisés

### Bonnes pratiques

```bash
# 1. Permissions strictes
chmod 600 ~/.config/nivuus/ha.conf

# 2. Ajouter au .gitignore
echo "~/.config/nivuus/ha.conf" >> ~/.gitignore

# 3. Utiliser des tokens séparés par usage
# Créer un token spécifique pour le CLI, un autre pour les scripts, etc.

# 4. HTTPS en production
HA_URL="https://ha.example.com:8123"

# 5. Vérifier régulièrement les tokens actifs
# Dans Home Assistant UI → Profile → Long-Lived Access Tokens
```

### Révocation de token

Si un token est compromis:

1. Aller dans Home Assistant → Profile
2. Scroller jusqu'à "Long-Lived Access Tokens"
3. Cliquer sur le token à révoquer
4. Supprimer le token
5. Créer un nouveau token et mettre à jour la config

## Intégration Nivuus

### Monitoring de la VM

Combiner avec WinRM pour monitorer la VM Windows et contrôler Home Assistant:

```bash
#!/bin/bash
# Surveiller température GPU et ajuster ventilation HA

GPU_TEMP=$(winvm 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits')

if [[ $GPU_TEMP -gt 75 ]]; then
    # Température élevée: allumer ventilateur
    ha service switch turn_on '{"entity_id": "switch.server_fan"}'
    ha service notify.mobile_app '{"message": "GPU temp high: ${GPU_TEMP}°C"}'
elif [[ $GPU_TEMP -lt 60 ]]; then
    # Température normale: éteindre ventilateur
    ha service switch turn_off '{"entity_id": "switch.server_fan"}'
fi
```

### Hooks système

Déclencher des actions Home Assistant lors d'événements système:

```bash
# /etc/systemd/system/vm-started.service
[Service]
ExecStart=/usr/local/bin/ha service notify.persistent_notification '{"message": "Windows VM started"}'

# Quand la VM démarre
ha service light turn_on '{"entity_id": "light.server_indicator", "rgb_color": [0, 255, 0]}'

# Quand la VM s'arrête
ha service light turn_off '{"entity_id": "light.server_indicator"}'
```

## Références

- [Home Assistant REST API Documentation](https://developers.home-assistant.io/docs/api/rest/)
- [Home Assistant Services](https://www.home-assistant.io/docs/scripts/service-calls/)
- [Jinja2 Templating](https://www.home-assistant.io/docs/configuration/templating/)
- [Long-Lived Access Tokens](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token)

## Support

Pour les problèmes:

1. Vérifier la connexion: `curl -I $HA_URL`
2. Tester le token: `ha config`
3. Voir les logs HA: Settings → System → Logs
4. Vérifier l'API: `ha raw /api/`

---

**Note:** Ce CLI utilise l'API REST de Home Assistant qui nécessite un token d'authentification. Gardez vos tokens sécurisés et ne les partagez jamais.
