# ScamRadar — Hyperlocal Community Fraud Radar

> **"Know the scam before it costs you."**
> A real, runnable, privacy-conscious community defense application designed to identify suspicious messages, explain digital deception techniques, and map fraud attempts across local neighborhoods.

---

## 🛡️ Synthetic Data Notice

> [!IMPORTANT]
> **Synthetic demo data — not real-world incident reports.**
> Pre-seeded records in ScamRadar are synthetically generated for demonstration and evaluation purposes. Locations are approximate neighborhood centroids to protect privacy. ScamRadar never claims that a community report represents a legally proven conviction.

---

## 🌟 The Problem & The Solution

- **The Problem**: Digital fraud in India has skyrocketed—from fake electricity disconnection threats and bank KYC deactivations to fraudulent work-from-home tasks and postal redelivery scams. Most victims realize a message was fraudulent only *after* losing funds.
- **The Solution**: **ScamRadar** answers 4 critical questions in seconds:
  1. *Is this message suspicious?*
  2. *Why is it suspicious?*
  3. *What should I do right now?*
  4. *Are other people in my neighborhood reporting something similar?*

---

## 🚀 Core Features

1. **Local Explainable AI Scam Checker**:
   - Analyzes unexpected messages locally with deterministic rule-based NLP and weighted scoring.
   - Categorizes threats (Electricity Impersonation, Bank Impersonation, Job Scam, Fake Delivery, Prize Scam, Investment Scam, Phishing).
   - Identifies red flags (Urgency pressure, Disconnection threats, Payment links, Credential solicitation).
   - Generates plain-English reasoning and actionable safety recommendations.
   - *AI assessment — not guaranteed truth.*
2. **Interactive Community Scam Map**:
   - Powered by Leaflet and OpenStreetMap.
   - Visualizes reported incidents across Hyderabad neighborhoods (Madhapur, Banjara Hills, Gachibowli, Ameerpet, Hitec City, etc.).
   - Risk-coded markers (High Risk, Medium Risk, Watch).
   - Preserves privacy by using approximate neighborhood coordinates with jitter—never exact street addresses.
3. **Dynamic Community Threat Alerts**:
   - Clustered intelligence by category and locality.
   - Uses responsible, non-sensational wording (*"Multiple community reports with similar patterns have been received in this area"*).
4. **Persistent SQLite Storage**:
   - All community reports and preferences persist across page reloads, browser restarts, and server reboots.
5. **Zero Credential Exposure**:
   - Strict design guardrails: never asks for, displays, or stores passwords, PINs, OTPs, or bank account numbers.

---

## 💻 Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Cybersecurity Design System with responsive grid, glassmorphic accents, and accessible multi-attribute badges), Vanilla JavaScript (ES6+ Single-Page Architecture).
- **Mapping**: Leaflet.js + OpenStreetMap.
- **Backend**: Python 3.13 + Flask 3.1.
- **Database**: SQLite3 (`data/scamradar.db`).
- **AI/NLP Engine**: Local rule-based NLP with weighted risk scoring and regex pattern detection (Offline, free, explainable, zero external API keys).

---

## 📂 Project Structure

```text
scamradar/
├── app.py                  # Flask web server & REST API endpoints
├── database.py             # SQLite schemas, synthetic seeding, geocoding & alerts
├── ai_engine.py            # Local explainable rule-based scam detection engine
├── requirements.txt        # Python dependencies
├── README.md               # Documentation & Hackathon guide
├── .gitignore              # Git ignore rules
│
├── app/
│   ├── templates/
│   │   └── index.html      # Responsive Single Page Application
│   │
│   └── static/
│       ├── styles.css      # Cybersecurity UI design system & responsive styles
│       └── app.js          # SPA routing, state, Leaflet integration, API calls
│
└── data/
    └── scamradar.db        # Persistent SQLite database
```

---

## ⚡ Quick Start & Run Instructions

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Setup (Windows PowerShell / CMD)
```powershell
# Navigate to the project root
cd d:\Scamrader

# Optional: Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start the application
python app.py
```

### 3. Open in Browser
Open your browser and visit:
```text
http://127.0.0.1:5000
```

---

## 🧪 Critical End-to-End User Journey (Demo Script)

Follow this 2-minute walkthrough to verify the complete journey:

1. **Dashboard Overview**:
   - Observe live metrics loaded from SQLite (Total Reports, High Risk, Medium Risk, Active Alerts).
   - Review recent reports with the *"Synthetic Demo Data"* tags.
2. **AI Scam Checker**:
   - Click **"Check a Scam"** in the navigation.
   - Click the quick example button: **"⚡ Electricity scam"** (or paste: *"Your electricity connection will be disconnected today. Pay ₹2,500 immediately using the following link to avoid service interruption: http://bit.ly/ts-power-bill"*).
   - Click **"Analyze with AI"**.
   - Watch the multi-stage progression: *Analyzing message... → Checking scam patterns... → Identifying red flags...*
   - Verify result: **HIGH RISK (90+/100)** with red flags: *Urgency Pressure, Threat of Service Closure, Unsolicited Payment Demand, Suspicious Link*.
   - Review the explanation and actionable safety checklist.
3. **Report to Community**:
   - Click **"Report this scam to community"**.
   - Note how the category, description, and risk evaluation auto-populate into the report form.
   - Select an approximate neighborhood (e.g., **Madhapur**).
   - Confirm the privacy guarantee checkbox.
   - Click **"Submit Community Report"**.
   - Notice the confirmation message: *"Report added successfully. Your report can help warn other people in your community."*
4. **Verify Database Persistence & Map Update**:
   - Open **"Scam Map"** to see the new marker pinned in Madhapur.
   - Return to **"Dashboard"** to verify that Total Reports and High Risk counters have incremented by 1.
   - Navigate to **"Alerts"** to see updated community alert clusters.
   - Refresh the browser (`F5`) or restart Flask to verify the report persists in `scamradar.db`.

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the single-page application |
| `GET` | `/api/stats` | Returns total reports, high risk, medium risk, active alerts, and recent feed |
| `GET` | `/api/reports` | Returns list of reports (supports `category`, `risk_level`, `area`, `limit`) |
| `POST` | `/api/reports` | Submits a new community report; auto-scores risk and triggers alert refresh |
| `POST` | `/api/analyze` | Local explainable AI evaluation of suspicious text |
| `GET` | `/api/alerts` | Returns dynamic community threat clusters |
| `GET` | `/api/settings` | Gets user neighborhood watch preferences |
| `POST` | `/api/settings` | Updates user neighborhood preferences |

---

## 🔒 Privacy & Safety Principles

1. **No Sensitive Data Collected**: ScamRadar strictly forbids requesting or storing passwords, ATM PINs, OTPs, CVVs, or bank account credentials.
2. **Approximate Localities Only**: Coordinates are mapped to neighborhood centroids with random jitter for privacy. Exact home addresses are never requested or displayed.
3. **Responsible Wording**: The platform uses non-sensational phrasing (*"Potential risk"*, *"Community report"*, *"AI assessment — not guaranteed truth"*).
4. **Local Execution**: The AI engine runs completely offline with transparent, explainable logic—no personal data is transmitted to third-party AI APIs.

---

## 🔮 Future Roadmap (Post-Hackathon)

- **TF-IDF Campaign Clustering**: Semantic similarity clustering to link related spam campaigns across multiple cities.
- **Multilingual Support**: Hindi, Telugu, Tamil, and other regional Indian language pattern detectors.
- **OCR Image Analysis**: Screenshot scanning for WhatsApp forward scam warnings.
- **Official Utility Verification Feeds**: Direct API integration with discoms (e.g. TSSPDCL) to check official bill due statuses.
