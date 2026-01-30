## 📦 Installation Steps

### 1️⃣ Clone Repository
```bash
git clone https://github.com/ayoubachak/vector-cm.git
cd vector-cm
```

### 2️⃣ Backend Setup
```bash
cd backend

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
# Edit .env and add your Google API key:
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
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### 5️⃣ Generate Dataset
```bash
cd ../data
python generate_ultimate_dataset.py
```

**Expected output:** 2000 clients + 200 fraud patterns

### 6️⃣ Populate Qdrant
```bash
cd ..
python populate_qdrant.py
```

**Expected output:** 
- credit_history_memory: 2000 points
- fraud_patterns: 200 points
- temporal_risk_memory: ~5400 points

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

## 🎯 Testing the Application

### Open in Browser

Navigate to: `http://localhost:5173`

### Test Flow

1. **Landing Page** - Choose Client Portal or Admin Dashboard
2. **Admin Dashboard** - Test search functionality
3. **Credit Oracle** - Check AI explanations appear
4. **Fraud Detection** - Upload test data
5. **Temporal Evolution** - View client journey over time



TODO: bouton approve/decline
client portal: enter id -> response
parse ai's responses
