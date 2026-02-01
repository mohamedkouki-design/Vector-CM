# 🏦 Vector Credit Memory (Vector CM)

**Self-Evolving Multimodal Credit Intelligence for MENA Informal Economy**

## Project Contributors
- **Mohamed Kouki** | **Ayoub Boudhrioua** | **Oussema Chihi** | **Aziz Ben Daali**

---

## 📋 Project Overview & Objectives

**Vector Credit Memory** is a production-ready credit intelligence system designed specifically for the MENA informal economy. The platform leverages vector embeddings and Qdrant's vector database for fast similarity search to enable real-time credit decisions without traditional credit scores.

### Key Objectives
✅ Democratize credit access for unbanked informal sector workers  
✅ Mitigate fraud through behavioral pattern matching  
✅ Provide personalized improvement paths for better credit outcomes  
✅ Enable transparent decisions with explainable AI (financial twins)  
✅ Process applications in real-time with <100ms latency  

### Innovation Highlight
Uses **Qdrant vector database** with semantic embeddings to find "financial twins"—similar clients who successfully repaid loans—providing both approval decisions and actionable improvement recommendations.

---

## 🌐 Platform Link

**Deployment Status**:
- **Frontend**: React + Vite (http://localhost:5173)
- **Backend API**: FastAPI (http://localhost:8000)
- **API Docs**: http://localhost:8000/docs
- **Vector DB**: Qdrant Dashboard (http://localhost:6333/dashboard)


---

## 🛠️ Technologies Used

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Backend** | Python | 3.8+ | Core language |
| | FastAPI | Latest | Async web framework |
| | Uvicorn | Latest | ASGI server |
| **Vector DB** | Qdrant | 1.x | Vector similarity search |
| | sentence-transformers | Latest | Text embeddings (all-MiniLM-L6-v2, 384D) |
| **Data Processing** | Pandas | Latest | Data manipulation |
| | NumPy | Latest | Numerical operations |
| | PyTorch | Latest | Deep learning framework |
| | Transformers | Latest | CLIP model for document analysis |
| **Frontend** | React | Latest | UI framework |
| | Vite | Latest | Build tool & dev server |
| | Tailwind CSS | Latest | Styling framework |
| | Axios | Latest | HTTP client |
| | TanStack React Query | Latest | Server state management |
| | Lucide React | Latest | Icon library |
| **ML/AI** | Google Generative AI | Latest | Credit oracle insights |
| **Image Processing** | OpenCV | Latest | Document processing |
| | Pillow | Latest | Image manipulation |
| **Infrastructure** | Docker | Latest | Containerization (Qdrant) |
| | Git/GitHub | - | Version control |

---

## 🏗️ Architecture & Project Hierarchy

### High-Level System Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Frontend (React + Vite @ localhost:5173)               │
│  ├─ Dashboard (Overview & Analytics)                    │
│  ├─ ClientPortal (Apply for Credit / Check Status)      │
│  └─ AdminDashboard (Analysis & Vector Space Explorer)   │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/REST (Axios)
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Backend (FastAPI @ localhost:8000)                     │
│  ├─ /api/v1/applications/* (Submit, Status, Update)     │
│  ├─ /api/v1/search/* (Similarity Search)                │
│  ├─ /api/v1/fraud/* (Fraud Detection)                   │
│  └─ /api/v1/counterfactual/* (What-If Scenarios)        │
└────────────────────┬─────────────────────────────────────┘
                     │ gRPC/TCP
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Qdrant Vector DB (Port 6333)                           │
│  ├─ credit_history_memory (384D vectors)                │
│  ├─ fraud_patterns_engine (384D vectors)                │
│  └─ document_risk_engine (512D CLIP vectors)            │
└──────────────────────────────────────────────────────────┘
```

### Project Directory Structure

```
Vector-CM/
├── backend/                              # FastAPI Backend
│   ├── main.py                          # FastAPI app entry point
│   ├── api/routers/
│   │   ├── applications.py              # Credit application endpoints
│   │   ├── fraud.py                     # Fraud detection endpoints
│   │   ├── counterfactual.py            # What-if scenario endpoints
│   │   ├── search.py                    # Vector similarity search
│   │   └── ...
|   ├── doc_check/
│   │   ├── dataset/fakes                # Generated fakes
│   │   ├── fake_gen.py
│   │   └── ...
│   ├── services/
│   │   ├── embeddings.py                # Vector generation (Sentence Transformers)
│   │   ├── qdrant_manager.py            # Qdrant operations (search, create, update)
│   │   ├── credit_oracle.py             # LLM-based credit analysis
│   │   └── utils.py                     # Helper functions
│   ├── models/schemas.py                # Pydantic data validation
│   ├── requirements.txt                 # Python dependencies
│   └── .env                             # Configuration (Qdrant, API keys)
│
├── frontend/                             # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx                      # Main router
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx            # Overview dashboard
│   │   │   ├── ClientPortal.jsx         # Client application portal
│   │   │   └── AdminDashboard.jsx       # Admin command center
│   │   ├── components/
│   │   │   ├── Galaxyview.jsx           # 2D vector space visualization
│   │   │   ├── CounterfactualEngine.jsx # What-if scenarios UI
│   │   │   ├── FraudAlert.jsx           # Fraud detection display
│   │   │   ├── AnimatedBackground.jsx   # Visual effects
│   │   │   └── ...
│   │   ├── services/api.js              # Axios API client
│   │   └── index.css                    # Global styles
│   ├── package.json                     # NPM dependencies
│   ├── vite.config.js                   # Vite configuration
│   ├── tailwind.config.js               # Tailwind CSS config
│   └── index.html                       # HTML entry point
│
├── data/                                 # Data & Scripts
│   ├── generate_data.py                 # Synthetic data generator
│   └── synthetic_*.csv                  # Generated datasets
├── populate_qdrant.py                   # Populating credit_history_memory , temporal_risk_memory and fraud_patterns collections
├── ingest_fakes.py                      # Populating document_risk_engine collection
│
└── README.md                             # This file
```

---

## 🗄️ Qdrant Integration (Deep Dive)

### Why Qdrant?

✅ **Sub-millisecond similarity search** on vectors  
✅ **Payload filtering** for complex queries  
✅ **Scalable** to millions of vectors  
✅ **Production-ready** with API security  
✅ **Managed cloud option** available  

### Three Vector Collections

#### 1️⃣ **credit_history_memory** (384D)
Stores historical client profiles and outcomes.

```python
Collection Schema:
{
  "client_id": "string",
  "archetype": "market_vendor|craftsman|etc",
  "years_active": 0-120,
  "monthly_income": 0-5000 (TND),
  "debt_ratio": 0-1,
  "payment_regularity": 0-1,
  "income_stability": 0-1,
  "mobile_payment_ratio": 0-1,
  "ledger_quality": 0-1,
  "outcome": "pending|approved|rejected",
  "actual_outcome": "optional string",
  ...
}
```

#### 2️⃣ **fraud_patterns_engine** (384D)
Stores known fraud behavioral patterns.

```python
Collection Schema:
{
"fraud_id":"FRAUD_0000"
"fraud_type":"shell_company"
"archetype":"gig_worker"
"debt_ratio":0.939
"income_stability":0.261
"fraud_narrative":"Company registered 2 weeks before loan application…"
"fraud_indicators":"suspicious_activity"
}
```

#### 3️⃣ **document_risk_engine** (512D CLIP)
Stores forged/authentic document patterns using CLIP embeddings.

```python
Collection Schema:
{
  "document_type": "invoice|receipt|id|etc",
  "authenticity_score": 0-1,
  "forgery_indicators": [list of anomalies]
}
```

### How Similarity Search Works

```python
# Step 1: Client applies with profile
client_data = {
    "archetype": "market_vendor",
    "debt_ratio": 0.45,
    "years_active": 15,
    "income_stability": 0.85,
    "payment_regularity": 0.88,
    "monthly_income": 2500,
    ...
}

# Step 2: Backend generates embedding (384D)
embedding = create_embedding(client_data)

# Step 3: Query Qdrant for similar clients
results = qdrant.query_points(
    collection="credit_history_memory",
    query=embedding,
    limit=50,
    score_threshold=0.70
)

# Step 4: Calculate weighted approval likelihood
approved_count = sum(1 for r in results if r.outcome == "approved")
approval_probability = approved_count / len(results)

# Step 5: Return decision with confidence
{
    "status": "approved",
    "confidence": 0.87,
    "similar_clients": 47,
    "success_rate": 0.89,
    "recommendation": "Likely to repay (matched with similar successful clients)"
}
```

### Similarity Metric
- **Distance**: Cosine Distance (0-2 scale, lower = more similar)
- **Conversion**: similarity = 1 - (distance / 2)
- **Matching**: Clients with similarity > 0.70 are considered similar




---

## 📦 Installation Steps

### 1️⃣ Clone Repository
```bash
git clone https://github.com/mohamedkouki-design/Vector-CM.git
cd vector-cm
```

### 2️⃣ Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cd backend
# Create a .env file and add your Google API key:
# GOOGLE_API_KEY=your-actual-key-here
```

### 3️⃣ Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Setup environment variables
```

### 4️⃣ Start Qdrant Database
```bash
# In a new terminal
# For Linux:
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
# For Windows:
docker run -p 6333:6333 -p 6334:6334 `
    -v ${PWD}/qdrant_storage:/qdrant/storage:Z `
    qdrant/qdrant
```

### 5️⃣ Generate Dataset
```bash
cd ../data/
python generate_data.py
cd ../backend/doc_check/
python fake_gen.py
```

### 6️⃣ Populate Qdrant
```bash
cd ../..
python populate_qdrant.py
python ingest_fakes.py
```

### 7️⃣ Start Backend
```bash
cd backend
python main.py
```

**Should see:** `Uvicorn running on http://0.0.0.0:8000`

### 8️⃣ Start Frontend
```bash
# In new terminal
cd frontend
npm run dev
```

**Should see:** `Local: http://localhost:5173`

---

## Testing the Application

### Verify Installation
```bash
# Health checks
curl http://localhost:8000/health        # Backend
curl http://localhost:6333/health        # Qdrant
```
### Open in Browser

Navigate to: `http://localhost:5173`

### Test Flow

1. **Landing Page** - Choose Client Portal or Admin Dashboard
2. **Admin Dashboard** - Test search functionality
3. **Credit Oracle** - Check AI explanations appear
4. **Fraud Detection** - Upload test data
5. **Temporal Evolution** - View client journey over time



---

## 📝 Usage Examples

### Example 1: Submit Credit Application

**Frontend (Client Portal)**
1. Navigate to http://localhost:5173 → "Apply for Credit"
2. Select **Manual Entry** mode
3. Fill business profile:
   - Business Type: Market Vendor
   - Years Active: 15
   - Debt Ratio: 45%
   - Payment Regularity: 88%
   - Monthly Income: 2,500 TND
4. Click "Submit Application"

**Backend Processing**
```bash
POST http://localhost:8000/api/v1/applications/submit
{
  "client_id": "CLIENT_0001",
  "archetype": "market_vendor",
  "years_active": 15,
  "debt_ratio": 0.45,
  "payment_regularity": 0.88,
  "monthly_income": 2500,
  ...
}
```

### Example 2: Check Application Status

**Frontend**
1. Go to Client Portal → "Check Status"
2. Enter your Client ID: `CLIENT_0001`
3. See result with approval/rejection status

**API Call**
```bash
GET http://localhost:8000/api/v1/applications/status/CLIENT_0001

Response:
{
  "client_id": "CLIENT_0001",
  "status": "approved",
  "rejection_reason": null
}
```

### Example 3: Analyze What-If Scenario

**Frontend (Admin Dashboard)**
1. Access Admin Command Center
2. Select "Counterfactual Engine"
3. Modify parameters: "What if the debt ratio dropped by 30%?"
4. See approval likelihood change to 92%

**API Call**
```bash
POST http://localhost:8000/api/v1/counterfactual/analyze
{
  "base_client": {...},
  "modifications": {"debt_ratio": 0.30}
}

Response:
{
  "original_approval_rate": 0.87,
  "modified_approval_rate": 0.92,
  "impact": "+5% approval likelihood"
}
```

### Example 4: View Financial Twins

**Frontend**
1. Dashboard → Search similar clients
2. System displays 50 most similar profiles
3. Color-coded by outcome (green = successful, red = default)
4. See exact similarity scores

---

## 🐛 Troubleshooting

**Qdrant Connection Refused?**
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

**Missing Python Dependencies?**
```bash
pip install -r requirements.txt --upgrade
```

**API Returns 500 Error?**
```bash
# Check backend logs for detailed error messages
# Verify .env file has GOOGLE_API_KEY set
```

**Frontend Not Loading?**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📜 License

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
