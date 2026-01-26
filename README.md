# 🧠 VectorCM

## Team Members

**Project Team:**
- **Mohamed Kouki** 
- **Ayoub Boudhrioua**
- **Oussema Chihi**
- **Aziz Ben Daali**

## Project Overview

**Vector Credit Memory** is a self-evolving multimodal credit intelligence system designed for the MENA informal economy. It leverages vector embeddings and similarity search to assess credit risk, detect fraud, and provide personalized financial guidance to informal sector workers.

The system uses Qdrant vector database for fast similarity matching against historical lending data, enabling real-time credit decisions and fraud pattern detection without traditional credit scores.

## Key Features

- **Vector-Based Credit Assessment**: Similarity search against 2,000+ historical cases to predict repayment likelihood
- **Fraud Detection**: Behavioral pattern matching to identify suspicious applications without label leakage
- **Success Twin Algorithm**: Finds similar clients who successfully repaid loans and provides personalized improvement paths
- **Weighted Approval Logic**: Outcomes weighted by similarity scores for more accurate predictions
- **Informal Economy Focus**: Specialized handling of mobile payment data, business seniority, ledger quality, and self-employment patterns
- **Multi-Dashboard Interface**: Overview, Client Portal, and Admin Command Center
- **What-If Counterfactuals**: Scenario analysis to show clients how to improve their approval chances

## Tech Stack

### Backend & Data
- **Python 3.8+** - Core language
- **Pandas** - Data processing and analysis
- **NumPy** - Numerical computations
- **Qdrant Vector Database** - Fast vector similarity search (11D vectors)
- **Sentence Transformers** - Text embeddings (for semantic analysis)

### Frontend
- **Streamlit** - Interactive web dashboard
- **Plotly** - Data visualization
- **Pandas DataFrame Display** - Tabular data rendering

### Core Libraries
- `qdrant-client` - Vector database client
- `sentence-transformers` - Text embedding model (all-MiniLM-L6-v2)
- `faker` - Synthetic data generation for testing
- `plotly.express` & `plotly.graph_objects` - Advanced charting

### Development Tools
- Git & GitHub - Version control
- Environment variables - Configuration management (.env)

## Architecture

```
app.py (Streamlit UI)
    ↓
qdrant_manager.py (Vector database operations)
    ↓
embeddings.py (11D vector generation)
    ↓
Qdrant Database
    ├── client_states (historical good/bad outcomes)
    └── fraud_patterns (known fraud behaviors)
    
demo_data.py (Synthetic data generation)
    ↓
CSV files (synthetic_clients.csv, synthetic_frauds.csv)
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Qdrant instance (local or cloud)
- Environment variables configured

### 2. Installation

```bash
# Clone repository
git clone https://github.com/mohamedkouki-design/Vector-CM.git
cd Vector-CM

# Install dependencies
pip install -r requirements.txt

# Additional packages if needed
pip install faker sentence-transformers qdrant-client streamlit plotly
```

### 3. Configuration

Create a `.env` file in the project root:

```bash
# Qdrant Configuration
QDRANT_LINK=http://localhost:6333  # Local Qdrant instance or cloud URL
QDRANT_API_KEY=your_api_key_here   # API key if using Qdrant Cloud
```

### 4. Generate Synthetic Data

```bash
python demo_data.py
```

This generates:
- `synthetic_clients.csv` - 2,000 historical client profiles
- `synthetic_frauds.csv` - ~100 known fraud patterns

### 5. Initialize Vector Database

```bash
python qdrant_manager.py
```

This creates Qdrant collections and loads data:
- `client_states` collection (11D vectors)
- `fraud_patterns` collection (11D vectors)

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Running the System

### Quick Start
```bash
# One-time setup
python demo_data.py
python qdrant_manager.py

# Run application
streamlit run app.py
```

### Dashboards Available

1. **🏠 Overview Dashboard**
   - System statistics (total cases, good payers, defaulters, fraud patterns)
   - Outcome distribution visualization
   - Income vs Debt scatter plot
   - Key performance metrics

2. **👤 Client Portal**
   - Credit application submission
   - Demo scenarios (Strong/Borderline/High-Risk/Fraud profiles)
   - Real-time approval likelihood assessment
   - Financial twins analysis
   - Personalized improvement recommendations

3. **⚙️ Admin Command Center**
   - Vector space explorer (2D projection)
   - System statistics and distribution analysis
   - What-If Counterfactual Engine for scenario analysis

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit main application with all dashboards |
| `qdrant_manager.py` | Vector database operations and similarity search |
| `embeddings.py` | 11D vector generation (behavioral features only) |
| `demo_data.py` | Synthetic data generator for testing |
| `utils.py` | Helper functions (success twin, improvement path) |
| `document_checker.py` | Basic document authenticity checking |
| `requirements.txt` | Python dependencies |

## How It Works

### 1. Vector Generation (11 Dimensions)
```
[income, expenses, debt, age, seniority, consistency, loan_amount, 
 employment_type, mobile_payment, ledger_quality, risk_score]
```

**Key Design**: `is_fraud` is NOT included to avoid false positives on high-consistency clients.

### 2. Similarity Search
When a new client applies:
1. Their profile is embedded as an 11D vector
2. Qdrant finds 20 most similar clients using COSINE distance
3. Outcomes are weighted by similarity scores
4. Weighted approval likelihood = Σ(similarity × outcome) / Σ(similarity)

## Vector Dimension Explanation

**11 Dimensions Used:**
1. **Income** (0-5000 normalized) - Monthly business income
2. **Expenses** (0-5000 normalized) - Monthly expenses
3. **Debt** (0-10000 normalized) - Total outstanding debt
4. **Age** (0-100 normalized) - Client age
5. **Seniority** (0-120 months normalized) - Business operating period
6. **Payment Consistency** (0-1) - Historical payment reliability
7. **Loan Amount** (0-15000 normalized) - Requested credit
8. **Employment Type** (0-1) - Formal/Mixed/Informal classification
9. **Mobile Payment Ratio** (0-1) - Digital payment adoption
10. **Ledger Quality** (0-1) - Record-keeping quality
11. **Risk Score** (0-1) - Calculated financial health indicator

**Not Included**: `is_fraud` label (to prevent false positives)

## Data Structure

### Client Profile
```python
{
    'client_id': 'TND-00001',
    'job_type': 'Market Vendor',
    'location': 'Tunis',
    'income': 1200,
    'expenses': 900,
    'debt': 1500,
    'age': 35,
    'seniority_months': 24,
    'payment_consistency': 0.75,
    'loan_amount': 2500,
    'employment_type': 'informal',
    'mobile_payment_ratio': 0.5,
    'ledger_quality_score': 0.6,
    'outcome': 1,  # 1 = good payer, 0 = defaulter
    'outcome_label': 'Good Payer',
    'risk_score': 0.72,
    'is_fraud': 0,
    'timestamp': '2025-12-15T...'
}
```

## Fraud Pattern Detection

Fraudsters typically show:
- **Income**: $5,000-12,000 (unrealistic for informal sector)
- **Consistency**: 95-100% (too perfect)
- **Debt**: $0-500 (suspiciously low)
- **Seniority**: 1-6 months (too young)
- **Loan Request**: $10,000-20,000 (high for claimed income)
- **Mobile Payment**: Extremes (0.0 or 0.95+, not natural)

## Demo Scenarios

The system includes 4 pre-configured test profiles:

1. **✅ Strong Profile** - Likely approved (92% consistency, established)
2. **⚠️ Borderline Profile** - Needs improvement (75% consistency, moderate debt)
3. **❌ High-Risk Profile** - Likely rejected (65% consistency, high debt-to-income)
4. **🚨 Fraud Attempt** - Should be flagged ($8000 income, perfect consistency, minimal debt)

## Testing

```bash
# Test embeddings
python embeddings.py

# Test vector database
python qdrant_manager.py

# Run Streamlit app
streamlit run app.py

# Try demo scenarios
# Select from Client Portal → Choose demo scenario → Submit Application
```

## Troubleshooting

### Qdrant Connection Issues
```python
# Verify Qdrant is running
# Local: http://localhost:6333
# Cloud: Check QDRANT_LINK and QDRANT_API_KEY in .env
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Vector Dimension Mismatch
- Ensure `embeddings.py` uses 11D
- Check `qdrant_manager.py` vector_dimension = 11
- Clear and rebuild collections if changed