# 🧠 Vector Credit Memory (Vector CM)

**Self-Evolving Multimodal Credit Intelligence for MENA Informal Economy**

## Team Members
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

**Deployment Status**: Available for Hackathon Judges
- **Frontend**: React + Vite (http://localhost:5173)
- **Backend API**: FastAPI (http://localhost:8000)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
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
  "rejection_reason": "optional string"
}
```

#### 2️⃣ **fraud_patterns_engine** (384D)
Stores known fraud behavioral patterns.

```python
Collection Schema:
{
  "fraud_type": "identity_fraud|income_falsification|etc",
  "risk_indicators": [list of flags],
  "confidence_score": 0-1,
  "pattern_description": "string"
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
    "monthly_income": 2500
}

# Step 2: Backend generates embedding (384D)
embedding = create_embedding(client_data)

# Step 3: Query Qdrant for similar clients
results = qdrant.search(
    collection="credit_history_memory",
    query_vector=embedding,
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

## ⚙️ Setup & Installation

### Prerequisites
- **Python 3.8+** 
- **Node.js 16+** (for frontend)
- **Qdrant 1.x** (local or cloud)
- **Git**

### Installation Steps

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/yourusername/Vector-CM.git
cd Vector-CM
```

#### **Step 2: Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Create .env file
cat > .env << EOF
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_google_api_key
HOST=0.0.0.0
PORT=8000
EOF

cd ..
```

#### **Step 3: Setup Frontend**
```bash
cd frontend
npm install
cd ..
```

#### **Step 4: Start Qdrant**
```bash
# Using Docker
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Verify: curl http://localhost:6333/health
```

#### **Step 5: Initialize Vector Collections**
```bash
cd backend
python -c "from services.qdrant_manager import QdrantManager; QdrantManager().create_collections()"
cd ..
```

#### **Step 6: Start Backend**
```bash
cd backend
python main.py
# 🚀 Uvicorn running on http://localhost:8000
```

#### **Step 7: Start Frontend** (new terminal)
```bash
cd frontend
npm run dev
# ✨ Vite dev server on http://localhost:5173
```

### Verify Installation
```bash
# Health checks
curl http://localhost:8000/health        # Backend
curl http://localhost:6333/health        # Qdrant
curl http://localhost:5173               # Frontend (open in browser)
```



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
  "client_id": "CLIENT_001",
  "archetype": "market_vendor",
  "years_active": 15,
  "debt_ratio": 0.45,
  "payment_regularity": 0.88,
  "monthly_income": 2500
}

Response (instant):
{
  "status": "approved",
  "confidence": 0.87,
  "similar_clients": 47,
  "success_rate": 0.89,
  "recommendation": "Strong profile matched with successful vendors"
}
```

### Example 2: Check Application Status

**Frontend**
1. Go to Client Portal → "Check Status"
2. Enter your Client ID: `CLIENT_001`
3. See result with approval/rejection status

**API Call**
```bash
GET http://localhost:8000/api/v1/applications/status/CLIENT_001

Response:
{
  "client_id": "CLIENT_001",
  "status": "approved",
  "rejection_reason": null
}
```

### Example 3: Analyze What-If Scenario

**Frontend (Admin Dashboard)**
1. Access Admin Command Center
2. Select "Counterfactual Engine"
3. Modify parameters: "What if debt ratio drops to 30%?"
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

## 🧪 Testing

```bash
# Test backend API
curl http://localhost:8000/api/v1/applications/submit -X POST \
  -H "Content-Type: application/json" \
  -d '{"archetype":"vendor","debt_ratio":0.45,...}'

# Test Qdrant connection
curl http://localhost:6333/health

# Test frontend (open browser)
open http://localhost:5173
```



---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application entry point |
| `backend/services/embeddings.py` | Vector generation (Sentence Transformers) |
| `backend/services/qdrant_manager.py` | Qdrant operations (search, create, update) |
| `backend/api/routers/applications.py` | Credit application endpoints |
| `frontend/src/pages/ClientPortal.jsx` | Client application & status check UI |
| `frontend/src/pages/AdminDashboard.jsx` | Admin analysis interface |
| `frontend/src/pages/Dashboard.jsx` | Overview statistics dashboard |
| `requirements.txt` | Python dependencies |

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
# Verify .env file has QDRANT_HOST and GOOGLE_API_KEY set
```

**Frontend Not Loading?**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```