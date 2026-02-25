# LLM-Beeldbeschrijver-API

> **Een productieklare Azure API voor hoogwaardige, Nederlandstalige schermbeschrijvingen op basis van screenshots.**

![CI](https://github.com/CedrickMakhlouf/LLM-Beeldbeschrijver-API/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Azure](https://img.shields.io/badge/cloud-Azure-0078D4)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Het Probleem

Voor blinden en slechtzienden zijn digitale schermen vaak slecht toegankelijk. Schermlezers bieden lineaire toegang, maar missen het overzicht en de context die ziende gebruikers wél ervaren. Handmatige beschrijvingen zijn arbeidsintensief en vaak niet up-to-date. Er is behoefte aan een automatische, kwalitatieve oplossing voor Nederlandstalige schermbeschrijvingen.

## De Oplossing

Deze API biedt een schaalbare, productieklare oplossing op Azure. Gebaseerd op de inzichten van de SEE-Benchmark, gebruikt de API geavanceerde Vision-Language Models (zoals GPT-4o of Llama via Azure) om screenshots automatisch om te zetten naar toegankelijke, Nederlandstalige beeldbeschrijvingen.

**Workflow:**
```
Screenshot (base64 of URL)
      │
      ▼
Azure Vision-Language Model (GPT-4o, Llama)
      │
      ▼
Nederlandstalige schermbeschrijving (API-response)
```

---

## Tech Stack

| Component        | Technologie                          |
|------------------|--------------------------------------|
| API              | FastAPI                              |
| Model-inferentie | Azure OpenAI / Azure AI Foundry      |
| Infrastructuur   | Azure Container Apps (Bicep IaC)     |
| Containerisatie  | Docker (multi-stage build)           |
| Code quality     | Ruff, Pytest                         |

---

## Projectstructuur

```
LLM-Beeldbeschrijver-API/
├── app/
│   ├── api/
│   │   ├── deps.py         # Dependency injection (VLMGenerator)
│   │   └── main.py         # FastAPI endpoints
│   ├── core/
│   │   ├── generator.py    # VLMGenerator: aanroepen van het VLM
│   │   └── settings.py     # Configuratie via pydantic-settings + .env
│   └── models/
│       └── schemas.py      # Request/response schema's
├── infra/
│   └── main.bicep          # Volledige Azure-infrastructuur als code
├── tests/
│   └── test_api.py
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── .env.example            # Vul je Azure credentials in
```

---

## Snelstart

### 1. Installeer afhankelijkheden

```bash
git clone https://github.com/CedrickMakhlouf/LLM-Beeldbeschrijver-API.git
cd LLM-Beeldbeschrijver-API

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Vul je Azure/OpenAI credentials in .env in
```

### 2. Configureer `.env`

```env
AZURE_OPENAI_ENDPOINT=https://<jouw-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<jouw-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### 3. Start de API lokaal

```bash
uvicorn app.api.main:app --reload
# Open: http://localhost:8000/docs
```

### 4. Stuur een screenshot naar de API

```bash
# Via URL
curl -X POST http://localhost:8000/api/describe \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/screenshot.png"}'

# Via base64
curl -X POST http://localhost:8000/api/describe \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "<jouw_base64_string>"}'
```

---

## Deploy op Azure (Infrastructure as Code)

De volledige Azure-omgeving (Container Apps, OpenAI, Log Analytics) is gedefinieerd in [`infra/main.bicep`](infra/main.bicep).

```bash
az group create --name rg-beeldbeschrijver --location westeurope

az deployment group create \
  --resource-group rg-beeldbeschrijver \
  --template-file infra/main.bicep \
  --parameters containerImage=<jouw-acr>/beeldbeschrijver-api:latest
```

---

## Docker

```bash
# Build
docker build -t beeldbeschrijver-api .

# Run
docker run -p 8000:8000 --env-file .env beeldbeschrijver-api
```

---

## Tests uitvoeren

```bash
pytest tests/ -v

# Inclusief integratietests (roept live Azure API aan)
pytest tests/ -v -m integration
```

---

## Architectuurkeuzes

| Keuze                    | Reden                                                       |
|--------------------------|-------------------------------------------------------------|
| Azure OpenAI / Foundry   | Enterprise-grade, schaalbaar, data blijft in Europa         |
| FastAPI                  | Snel, async, automatische OpenAPI-docs                      |
| Twee VLM-backends        | Flexibel inzetbaar: GPT-4o of open-source Llama             |
| Bicep IaC                | Reproduceerbaar, versiebeheerd, eenvoudig te deployen       |
| Docker multi-stage build | Kleine image, non-root gebruiker, productieveilig           |
| SEE-Benchmark            | Kwaliteitsstandaard voor de schermbeschrijvingsprompt       |

---

## Roadmap

- [ ] Ondersteuning voor meerdere talen
- [ ] Streaming responses via Server-Sent Events
- [ ] Automatische re-evaluatie via SEE-Benchmark koppeling
- [ ] Authenticatie (API-key middleware)

---

## Licentie

MIT
