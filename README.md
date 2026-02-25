# LLM Beeldbeschrijver API

> Zet een screenshot of publieke afbeelding-URL om in een toegankelijke schermbeschrijving in het Nederlands (Llama 4 Maverick, Azure).

![Python](https://img.shields.io/badge/python-3.12-blue)
![Azure](https://img.shields.io/badge/cloud-Azure-0078D4)
![License](https://img.shields.io/badge/license-MIT-green)

---

### 🚀 [Probeer de live demo op Azure →](https://see-benchmark.ambitiousmoss-cd4cf8a8.eastus.azurecontainerapps.io/docs)

> **Let op:** De demo gebruikt een publiek toegankelijke testafbeelding. Je kunt ook je eigen afbeelding-URL of base64 uploaden.

```bash
# Snel testen met curl (publieke afbeelding)
curl -X POST https://see-benchmark.ambitiousmoss-cd4cf8a8.eastus.azurecontainerapps.io/api/describe \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/MSFT-Microsoft-Edge-browser-window-RWN3c9?scl=1"}'
```

---

## 📌 Probleem & Doel

Slechtziende gebruikers zijn afhankelijk van schermlezers, die schermen lineair en fragmentarisch presenteren. Hierdoor missen ze het top-down overzicht dat zienden wél direct uit visuele cues halen. Ontwikkelaars leveren vaak onvoldoende metadata voor goede toegankelijkheid.  

**LLM Beeldbeschrijver API** maakt het mogelijk om automatisch, intelligent en consistent schermsamenvattingen te genereren met Vision-Language Models (VLMs). Dit helpt om de toegankelijkheidskloof te dichten en maakt digitale diensten inclusiever.

---

## Probleem

Veel schermlezers en gebruikers hebben moeite met ontoegankelijke screenshots. Handmatige beschrijvingen zijn traag en subjectief.  
**Automatische, consistente beeldbeschrijving is nodig voor echte digitale toegankelijkheid.**

## Oplossing

Een cloud-native API die elk screenshot of afbeelding-URL omzet naar een Nederlandse beschrijving via een Vision Language Model (Llama 4 Maverick):

```
Afbeelding (base64 of URL)
        │
        ▼
FastAPI (Python)
        │
        ▼
Azure AI Foundry (Llama 4 Maverick)
        │
        ▼
Beschrijving in het Nederlands
```

---

## Tech Stack

| Laag           | Technologie                        |
|----------------|------------------------------------|
| API            | FastAPI, Pydantic                  |
| VLM            | Azure AI Foundry (Llama 4 Maverick)|
| Infra          | Azure Bicep, Container Apps        |
| Container      | Docker                             |
| CI/CD/Test     | Pytest, python-dotenv              |

---

## Projectstructuur

```
SEE-Benchmark-v2/
├── app/
│   ├── api/        # FastAPI endpoints
│   ├── core/       # Generator, settings
│   └── models/     # Pydantic schemas
├── infra/          # Azure Bicep (IaC)
├── tests/          # Pytest tests
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Snel starten

### 1. Clone & installeer

```bash
git clone <repo-url>
cd SEE-Benchmark-v2
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Vul je Azure-keys in .env aan
```

### 2. Lokaal draaien

```bash
uvicorn app.api.main:app --reload
# Open: http://localhost:8000/docs
```

### 3. Test de API

Zie curl-voorbeeld bovenaan, of gebruik Swagger UI.

---

## Deployment (Azure)

Alle infra staat in [infra/main.bicep](infra/main.bicep).  
Zie de comments in het bestand voor parameters en uitrol.

---

## Testen

```bash
pytest
```

---

## Licentie

MIT – zie [LICENSE](LICENSE)
