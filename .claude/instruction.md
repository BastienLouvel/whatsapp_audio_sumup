# WhatsApp Audio Summarizer - Instructions Projet

## Architecture
Structure modulaire avec webhook server pour WhatsApp Business API.

```
WhatsApp Cloud API
        │
        ▼ (webhook POST)
   FastAPI Server ──► LLM (Claude/GPT/Gemini)
        │
        ▼ (API call)
   Réponse WhatsApp
```

### Modules principaux
- `webhook/` : Serveur FastAPI pour recevoir les webhooks WhatsApp
- `connectors/` : Client WhatsApp Business API (envoi messages, download media)
- `llm/` : Clients LLM interchangeables (Claude/GPT/Gemini)
- `config/` : Configuration et prompts par style

## Principes de Code

### 1. Abstraction LLM
- Utiliser une classe abstraite `BaseLLM` avec méthode `transcribe_and_summarize()`
- Pattern Factory pour instancier le bon client
- Chaque LLM hérite de `BaseLLM`

### 2. Configuration
- Toutes les API keys dans `.env` (jamais commité)
- `settings.py` charge les variables d'environnement
- `prompts.py` contient un dict de styles facilement extensible

### 3. Gestion des Styles
```python
STYLES = {
    "pro": "Résume de manière professionnelle...",
    "humoristique": "Résume avec humour...",
    "technique": "Résumé technique détaillé..."
}
```

### 4. Error Handling
- Try/except sur tous les appels API
- Logging avec niveau INFO pour le flow, ERROR pour les exceptions
- Réponse d'erreur envoyée à l'utilisateur WhatsApp si échec

### 5. WhatsApp Business API
- Webhook pour recevoir les messages entrants
- Download media pour récupérer les audios
- Send message pour répondre avec le résumé

## Dépendances
- `anthropic`, `openai`, `google-generativeai` - Clients LLM
- `fastapi`, `uvicorn` - Serveur webhook
- `httpx` - Client HTTP async pour WhatsApp API
- `python-dotenv` - Chargement des variables d'env

## Workflow
1. Audio reçu sur WhatsApp → webhook POST
2. Serveur télécharge l'audio via WhatsApp API
3. Audio envoyé au LLM sélectionné
4. Résumé généré avec style choisi
5. Résumé renvoyé sur WhatsApp en réponse

## Lancement
```bash
# Copier et configurer .env
cp .env.example .env

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
uvicorn webhook.server:app --host 0.0.0.0 --port 8000
```

## Configuration WhatsApp Business API

1. Créer une app sur [Meta Developer Portal](https://developers.facebook.com/)
2. Ajouter le produit WhatsApp
3. Récupérer : Phone Number ID, Access Token
4. Configurer le webhook URL : `https://your-domain.com/webhook`
5. S'abonner aux événements `messages`
