"""Constants for the Home Agent integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "home_agent"

# Platforms
PLATFORMS: Final = ["sensor"]

# Configuration keys
CONF_GEMINI_API_KEY: Final = "gemini_api_key"
CONF_GEMINI_MODEL: Final = "gemini_model"
CONF_CHECK_INTERVAL: Final = "check_interval"
CONF_CHROMA_URL: Final = "chroma_url"
CONF_NOTIFY_SERVICE: Final = "notify_service"

# Defaults
DEFAULT_GEMINI_MODEL: Final = "gemini-2.0-flash"
DEFAULT_CHECK_INTERVAL: Final = 15  # minutes
DEFAULT_SECURITY_INTERVAL: Final = 5  # minutes
DEFAULT_CHROMA_URL: Final = "http://localhost:8000"
DEFAULT_NOTIFY_SERVICE: Final = "mobile_app_pixel_10_pro"

# Available models
GEMINI_MODELS: Final = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
]

# Sensor keys
SENSOR_STATUS: Final = "status"
SENSOR_LAST_DECISION: Final = "last_decision"
SENSOR_ACTIONS_TODAY: Final = "actions_today"

# Service names
SERVICE_RUN_CHECK: Final = "run_check"
SERVICE_RUN_SECURITY_CHECK: Final = "run_security_check"
SERVICE_RUN_AUTOMATION_REVIEW: Final = "run_automation_review"

# States
STATE_IDLE: Final = "idle"
STATE_ANALYZING: Final = "analyzing"
STATE_EXECUTING: Final = "executing"
STATE_ERROR: Final = "error"

# Icons
ICON_AGENT: Final = "mdi:robot"
ICON_DECISION: Final = "mdi:head-lightbulb"
ICON_COUNTER: Final = "mdi:counter"

# Kill switch entity
KILL_SWITCH_ENTITY: Final = "input_boolean.home_agent_enabled"

# Notification guardrails
NOTIFICATION_RATE_LIMIT: Final = 5  # max per hour (periodic checks)
SECURITY_NOTIFICATION_RATE_LIMIT: Final = 10  # max per hour (security checks)
NOTIFICATION_DEDUP_COOLDOWN: Final = 30  # minutes — suppress identical messages

# ChromaDB collection
CHROMA_COLLECTION: Final = "home_agent_memories"

# Gemini response schema
RESPONSE_SCHEMA: Final = {
    "type": "object",
    "properties": {
        "analysis": {
            "type": "string",
            "description": "Résumé de l'analyse de la situation",
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "service_call",
                            "create_automation",
                            "disable_automation",
                            "notification",
                        ],
                    },
                    "service": {"type": "string"},
                    "entity_id": {"type": "string"},
                    "data": {"type": "object"},
                    "reason": {"type": "string"},
                },
                "required": ["type", "reason"],
            },
        },
        "alerts": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["analysis", "actions", "alerts"],
}

# System prompts
MAIN_PROMPT: Final = """Tu es l'agent IA autonome de la maison de Maxime. Tu agis sans demander confirmation.

## Maison
- Propriétaire: Maxime Allanic
- Chat: Soraya (distributeur automatique)
- Étages: RDC (Salon, Cuisine, Salle de bain), Mezzanine (Chambre)
- Chauffage: climate.radiateur (comfort/eco/off)
- Alarme: alarm_control_panel.maison
- Éclairage adaptatif avec sleep modes par pièce
- TV Philips avec Ambilight, 2 aspirateurs Valetudo, Peugeot e-208, Bambu Lab P1S

## Règles de sécurité
- Si Maxime est absent ET une porte/fenêtre s'ouvre → activer alarme + notification urgente
- Si alarme déclenchée → ne JAMAIS la désactiver automatiquement
- Si mouvement détecté + absence → notification immédiate
- Si batterie < 10% → notification critique
- Toujours verrouiller la porte d'entrée quand Maxime part

## Règles de confort
- Si Maxime rentre → allumer lumières salon, chauffage comfort, désactiver alarme
- Si Maxime part → éteindre toutes les lumières, chauffage eco, activer alarme
- La nuit (après 23h) → activer sleep modes adaptatifs, lumières très tamisées
- Au réveil (mouvement matin + lumière du jour) → désactiver sleep modes, lumières normales
- Si TV allumée le soir → baisser lumières salon pour ambiance cinéma

## Règles énergie
- Si personne à la maison depuis > 1h → chauffage eco
- Ne jamais couper le chauffage complètement en hiver (min eco)
- Si température extérieure > 22°C → chauffage off
- Si fenêtre ouverte → chauffage eco dans la pièce concernée
- Éteindre les lumières des pièces vides depuis > 10 min

## Interdits
- Ne JAMAIS désactiver l'alarme quand Maxime est absent
- Ne JAMAIS couper l'alimentation du distributeur du chat
- Ne JAMAIS modifier les automatisations critiques (alarme, sécurité)
- Ne JAMAIS envoyer plus de 5 notifications par heure (sauf urgence sécurité)
- Ne JAMAIS allumer toutes les lumières d'un coup

## Format de réponse
Réponds UNIQUEMENT en JSON selon le schema fourni. Pas de texte autour.
Pour les service_call, utilise le format: service="domain.service", entity_id="entity_id", data={...}
"""

SECURITY_PROMPT: Final = """Tu es le gardien de sécurité IA de la maison de Maxime. Check rapide sécurité uniquement.

## Vérifie
- Alarme: état actuel vs état attendu (absent=armée, présent=désarmée)
- Portes/fenêtres: ouvertures anormales pendant absence
- Mouvement: détection anormale pendant absence
- Batteries critiques: appareils < 15%

## Règles strictes
- JAMAIS désactiver l'alarme automatiquement
- Notification urgente si intrusion suspectée
- Notification si batterie critique

## Format
Réponds en JSON. Si tout est normal: actions=[], alerts=[].
"""

AUTOMATION_REVIEW_PROMPT: Final = """Tu es l'optimiseur d'automatisations de la maison de Maxime.

## Analyse les automatisations fournies et vérifie:
1. Automatisations jamais déclenchées depuis > 30 jours → suggérer désactivation
2. Automatisations en erreur → signaler
3. Automatisations redondantes → suggérer fusion
4. Automatisations manquantes → suggérer création

## Règles
- Ne JAMAIS toucher aux automatisations de sécurité/alarme
- Préférer modifier plutôt que supprimer
- Chaque suggestion doit avoir une raison claire

## Format
Réponds en JSON avec actions et alerts.
"""
