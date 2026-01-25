# demo_data.py - Production-ready data generator integrated with Vector Credit Memory
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker
fake = Faker()
np.random.seed(42)
random.seed(42)

# Configuration
NUM_SAMPLES = 2000
FRAUD_RATE = 0.05  # 5% fraudsters

# MENA Informal Economy Context
JOBS = ['Market Vendor', 'Carpenter', 'Plumber', 'Freelance Designer',
        'Street Food Vendor', 'Tailor', 'Private Tutor', 'Taxi Driver', 
        'Artisan', 'Electrician', 'Mechanic', 'Delivery Driver']

LOCATIONS = ['Tunis', 'Sfax', 'Sousse', 'Gabes', 'Ariana', 'Ben Arous', 
             'Bizerte', 'Nabeul']

# Employment type mapping for embedding consistency
EMPLOYMENT_MAP = {
    'Market Vendor': 'informal',
    'Carpenter': 'informal',
    'Plumber': 'informal',
    'Freelance Designer': 'mixed',
    'Street Food Vendor': 'informal',
    'Tailor': 'informal',
    'Private Tutor': 'mixed',
    'Taxi Driver': 'informal',
    'Artisan': 'informal',
    'Electrician': 'informal',
    'Mechanic': 'informal',
    'Delivery Driver': 'informal'
}

class VectorCMDataGenerator:
    """
    Generate realistic credit data fully integrated with Vector Credit Memory system
    Includes proper correlations, realistic ranges, and fraud patterns
    """
    
    def __init__(self):
        self.generated_ids = set()
        self.fraud_patterns = []
        
    def generate_client_profile(self, id_num, force_fraud=False):
        """Generate a single client profile with realistic correlations"""
        
        # Demographics
        job = random.choice(JOBS)
        location = random.choice(LOCATIONS)
        age = random.randint(21, 65)
        
        # Seniority correlates with age
        max_seniority = min((age - 21) * 12, 120)
        seniority_months = random.randint(1, max(12, max_seniority))
        
        # Base income varies by job type and seniority
        job_income_base = {
            'Market Vendor': (600, 1500),
            'Carpenter': (1000, 2500),
            'Plumber': (1200, 2800),
            'Freelance Designer': (1500, 4000),
            'Street Food Vendor': (500, 1200),
            'Tailor': (700, 1800),
            'Private Tutor': (800, 2000),
            'Taxi Driver': (1000, 2200),
            'Artisan': (900, 2500),
            'Electrician': (1100, 2600),
            'Mechanic': (1000, 2400),
            'Delivery Driver': (700, 1600)
        }
        
        income_min, income_max = job_income_base[job]
        # Seniority bonus: +5% per year up to 50%
        seniority_multiplier = 1 + min(0.5, (seniority_months / 12) * 0.05)
        base_income = random.randint(income_min, income_max) * seniority_multiplier
        
        # Decide if this is fraud
        is_fraud = force_fraud or (random.random() < FRAUD_RATE)
        
        if is_fraud:
            return self._generate_fraud_profile(id_num, job, location, age)
        
        # Normal profile generation
        # Mobile payment usage correlates with age (younger = more digital)
        age_digital_factor = 1 - ((age - 21) / 44) * 0.4  # 21yo=1.0, 65yo=0.6
        mobile_payment_usage = min(1.0, random.uniform(0.3, 1.0) * age_digital_factor)
        
        # Ledger quality correlates with seniority and education proxy
        ledger_score = min(1.0, random.uniform(0.4, 0.9) + (seniority_months / 120) * 0.3)
        
        # Expenses realistic to income (60-85% of income)
        expense_ratio = random.uniform(0.60, 0.85)
        monthly_expenses = base_income * expense_ratio
        
        # Debt correlates inversely with financial discipline
        financial_discipline = (ledger_score * 0.5 + mobile_payment_usage * 0.3 + 
                               (1 - expense_ratio) * 0.2)
        
        max_debt = base_income * random.uniform(0.5, 3.0) * (1 - financial_discipline * 0.5)
        current_debt = random.uniform(0, max_debt)
        
        # Payment consistency based on financial health
        income_after_expenses = base_income - monthly_expenses
        debt_burden = current_debt / max(1, base_income)
        
        payment_consistency = min(1.0, max(0.3,
            (income_after_expenses / base_income) * 0.4 +
            (1 - min(1, debt_burden)) * 0.3 +
            ledger_score * 0.2 +
            mobile_payment_usage * 0.1 +
            random.uniform(0, 0.2)
        ))
        
        # Loan amount requested (realistic to income)
        loan_multiplier = random.uniform(1.5, 4.0)
        requested_amount = min(15000, base_income * loan_multiplier)
        
        # Calculate risk score (for outcome determination)
        debt_to_income = current_debt / base_income
        savings_capacity = (base_income - monthly_expenses) / base_income
        
        risk_score = (
            payment_consistency * 0.35 +
            (1 - min(1, debt_to_income)) * 0.25 +
            savings_capacity * 0.20 +
            (seniority_months / 120) * 0.10 +
            ledger_score * 0.10
        )
        
        # Add realistic noise
        risk_score += random.uniform(-0.15, 0.15)
        risk_score = max(0, min(1, risk_score))
        
        # Determine outcome based on risk score
        if risk_score >= 0.65:
            outcome = 1  # Good Payer
            outcome_label = "Good Payer"
            risk_narrative = self._generate_good_narrative(job, ledger_score, 
                                                          mobile_payment_usage, seniority_months)
        elif risk_score >= 0.45:
            outcome = random.choice([0, 1])  # 50/50 Late Payer
            outcome_label = "Late Payer" if outcome == 0 else "Good Payer"
            risk_narrative = self._generate_moderate_narrative(job, ledger_score, 
                                                               income_after_expenses)
        else:
            outcome = 0  # Defaulter
            outcome_label = "Defaulter"
            risk_narrative = self._generate_poor_narrative(job, debt_burden, ledger_score)
        
        # Employment type
        employment_type = EMPLOYMENT_MAP.get(job, 'informal')
        
        # Generate timestamp (random over past 2 years)
        days_ago = random.randint(1, 730)
        timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        return {
            # Identity
            'client_id': f'TND-{id_num:05d}',
            'job_type': job,
            'location': location,
            'age': age,
            
            # Financial Core (for vector embedding)
            'income': round(base_income, 2),
            'expenses': round(monthly_expenses, 2),
            'debt': round(current_debt, 2),
            'seniority_months': seniority_months,
            'payment_consistency': round(payment_consistency, 3),
            'loan_amount': round(requested_amount, 2),
            'employment_type': employment_type,
            
            # Informal Economy Specific
            'mobile_payment_ratio': round(mobile_payment_usage, 3),
            'ledger_quality_score': round(ledger_score, 3),
            
            # Outcome
            'outcome': outcome,
            'outcome_label': outcome_label,
            'risk_score': round(risk_score, 3),
            
            # Explainability
            'risk_narrative': risk_narrative,
            
            # Metadata
            'is_fraud': 0,
            'timestamp': timestamp
        }
    
    def _generate_fraud_profile(self, id_num, job, location, age):
        """Generate suspicious fraud pattern"""
        
        # Fraud patterns: Unrealistic income, perfect consistency, low expenses
        fraudulent_income = random.randint(5000, 12000)  # Too high for informal
        fraudulent_expenses = fraudulent_income * random.uniform(0.15, 0.30)  # Too low
        
        # Young age + short seniority + high loan request = red flag
        fraud_age = random.randint(19, 26)
        fraud_seniority = random.randint(1, 6)
        
        # Perfect or near-perfect scores (too good to be true)
        fraud_consistency = random.uniform(0.95, 1.0)
        fraud_ledger = random.uniform(0.92, 1.0)
        
        # High loan request relative to (fake) income
        loan_request = random.randint(10000, 20000)
        
        # Minimal or zero debt (suspicious for informal worker)
        fraud_debt = random.uniform(0, 500)
        
        # Mobile payment at extremes
        fraud_mobile = random.choice([random.uniform(0.0, 0.2), random.uniform(0.95, 1.0)])
        
        fraud_narratives = [
            "Document inconsistencies detected: ID name mismatch with uploaded invoices. Sequential invoice numbers across different claimed vendors.",
            "Synthetic identity suspected: Perfect payment history with zero verifiable transaction trail. All documents uploaded within 24 hours.",
            "Velocity fraud pattern: Multiple applications from different IDs with identical handwriting in ledgers. Same phone number across profiles.",
            "Income fabrication detected: Declared income 300% above sector average. Bank statement shows different account holder name.",
            "Document forgery indicators: Invoice templates match known fake document database. Metadata shows recent creation despite claimed historical dates."
        ]
        
        timestamp = (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
        
        fraud_profile = {
            'client_id': f'FRAUD-{id_num:05d}',
            'job_type': job,
            'location': location,
            'age': fraud_age,
            'income': round(fraudulent_income, 2),
            'expenses': round(fraudulent_expenses, 2),
            'debt': round(fraud_debt, 2),
            'seniority_months': fraud_seniority,
            'payment_consistency': round(fraud_consistency, 3),
            'loan_amount': round(loan_request, 2),
            'employment_type': 'informal',
            'mobile_payment_ratio': round(fraud_mobile, 3),
            'ledger_quality_score': round(fraud_ledger, 3),
            'outcome': 0,  # Always defaulter
            'outcome_label': 'Fraud',
            'risk_score': 0.0,
            'risk_narrative': random.choice(fraud_narratives),
            'is_fraud': 1,
            'timestamp': timestamp
        }
        
        self.fraud_patterns.append(fraud_profile)
        return fraud_profile
    
    def _generate_good_narrative(self, job, ledger_score, mobile_usage, seniority):
        """Generate positive risk narrative"""
        narratives = [
            f"Steady cash flow verified via {'digital' if mobile_usage > 0.7 else 'handwritten'} ledger. {seniority} months operational history as {job} with consistent client base.",
            f"High-quality documentation provided. Mobile payment usage ({mobile_usage:.0%}) indicates strong digital literacy. Reliable income patterns observed.",
            f"Established {job} with {seniority} months seniority. Ledger quality score {ledger_score:.2f} shows organized financial management. Low debt-to-income ratio.",
            f"Strong informal credit history. Regular mobile money transactions align with declared income. Active business with repeat customer evidence."
        ]
        return random.choice(narratives)
    
    def _generate_moderate_narrative(self, job, ledger_score, income_after_expenses):
        """Generate moderate risk narrative"""
        narratives = [
            f"Seasonal income fluctuations typical for {job} sector. Ledger legible but shows recording gaps. Generally reliable with occasional liquidity constraints.",
            f"Moderate documentation quality (score: {ledger_score:.2f}). Income verifiable but irregular. Payment history shows delays during low season.",
            f"Acceptable risk profile for informal {job}. Limited savings buffer (${income_after_expenses:.0f}/month) may cause occasional late payments.",
            f"Mixed signals: Good seniority but inconsistent record-keeping. Requires monitoring but shows repayment intent."
        ]
        return random.choice(narratives)
    
    def _generate_poor_narrative(self, job, debt_burden, ledger_score):
        """Generate high-risk narrative"""
        narratives = [
            f"High debt-to-income ratio ({debt_burden:.1%}). Uploaded receipts illegible or missing dates. Limited verifiable transaction history.",
            f"Unverifiable income sources for {job}. Poor ledger quality (score: {ledger_score:.2f}). Multiple inconsistencies in documentation.",
            f"Critical financial stress indicators: Debt exceeds sustainable levels. No digital payment trail. Documentation quality insufficient for approval.",
            f"High-risk profile: Minimal business seniority, poor record-keeping, excessive debt burden. Approval not recommended without guarantor."
        ]
        return random.choice(narratives)
    
    def generate_dataset(self, n_samples=NUM_SAMPLES, fraud_rate=FRAUD_RATE):
        """Generate complete dataset"""
        
        print(f"🔄 Generating {n_samples} client profiles...")
        
        # Calculate fraud count
        n_frauds = int(n_samples * fraud_rate)
        n_legitimate = n_samples - n_frauds
        
        profiles = []
        
        # Generate legitimate profiles
        for i in range(n_legitimate):
            profile = self.generate_client_profile(i, force_fraud=False)
            profiles.append(profile)
            
            if (i + 1) % 500 == 0:
                print(f"   Generated {i + 1} legitimate profiles...")
        
        # Generate fraud profiles
        for i in range(n_frauds):
            profile = self.generate_client_profile(n_legitimate + i, force_fraud=True)
            profiles.append(profile)
        
        print(f"✅ Generated {n_legitimate} legitimate + {n_frauds} fraud profiles")
        
        return pd.DataFrame(profiles)
    
    def create_collections_data(self, df):
        """Split data into collections for Qdrant"""
        
        # Main client collection (all legitimate cases)
        clients_df = df[df['is_fraud'] == 0].copy()
        
        # Fraud patterns collection
        fraud_df = df[df['is_fraud'] == 1].copy()
        
        return clients_df, fraud_df


def main():
    """Generate and save all data"""
    
    print("=" * 60)
    print("Vector Credit Memory - Data Generation")
    print("=" * 60)
    
    generator = VectorCMDataGenerator()
    
    # Generate full dataset
    df = generator.generate_dataset(n_samples=NUM_SAMPLES, fraud_rate=FRAUD_RATE)
    
    # Split into collections
    clients_df, fraud_df = generator.create_collections_data(df)
    
    # Save files
    print("\n💾 Saving datasets...")
    
    # Full dataset
    df.to_csv('vector_cm_synthetic_data.csv', index=False)
    print(f"   ✅ vector_cm_synthetic_data.csv ({len(df)} records)")
    
    # Client collection (for Qdrant)
    clients_df.to_csv('synthetic_clients.csv', index=False)
    print(f"   ✅ synthetic_clients.csv ({len(clients_df)} records)")
    
    # Fraud collection (for Qdrant)
    fraud_df.to_csv('synthetic_frauds.csv', index=False)
    print(f"   ✅ synthetic_frauds.csv ({len(fraud_df)} records)")
    
    # Statistics
    print("\n📊 Dataset Statistics:")
    print("-" * 60)
    print(f"Total Samples: {len(df)}")
    print(f"\nOutcome Distribution:")
    print(df['outcome_label'].value_counts().to_string())
    
    print(f"\nEmployment Types:")
    print(clients_df['employment_type'].value_counts().to_string())
    
    print(f"\nFinancial Ranges (Legitimate Clients):")
    print(f"  Income: ${clients_df['income'].min():.0f} - ${clients_df['income'].max():.0f} (avg: ${clients_df['income'].mean():.0f})")
    print(f"  Debt: ${clients_df['debt'].min():.0f} - ${clients_df['debt'].max():.0f} (avg: ${clients_df['debt'].mean():.0f})")
    print(f"  Loan Requests: ${clients_df['loan_amount'].min():.0f} - ${clients_df['loan_amount'].max():.0f}")
    
    print(f"\nGood Payer Metrics:")
    good_payers = clients_df[clients_df['outcome'] == 1]
    print(f"  Count: {len(good_payers)} ({len(good_payers)/len(clients_df)*100:.1f}%)")
    print(f"  Avg Income: ${good_payers['income'].mean():.0f}")
    print(f"  Avg Debt: ${good_payers['debt'].mean():.0f}")
    print(f"  Avg Payment Consistency: {good_payers['payment_consistency'].mean():.2%}")
    print(f"  Avg Seniority: {good_payers['seniority_months'].mean():.0f} months")
    
    print(f"\nDefaulter Metrics:")
    defaulters = clients_df[clients_df['outcome'] == 0]
    print(f"  Count: {len(defaulters)} ({len(defaulters)/len(clients_df)*100:.1f}%)")
    print(f"  Avg Income: ${defaulters['income'].mean():.0f}")
    print(f"  Avg Debt: ${defaulters['debt'].mean():.0f}")
    print(f"  Avg Payment Consistency: {defaulters['payment_consistency'].mean():.2%}")
    
    print(f"\n🔍 Sample Records:")
    print("-" * 60)
    print(df[['client_id', 'job_type', 'income', 'debt', 'outcome_label']].head(10).to_string(index=False))
    
    print("\n" + "=" * 60)
    print("✅ Data generation complete! Ready for Qdrant ingestion.")
    print("=" * 60)
    
    # Create a quick summary JSON
    summary = {
        'total_records': len(df),
        'legitimate_clients': len(clients_df),
        'fraud_cases': len(fraud_df),
        'good_payers': int((clients_df['outcome'] == 1).sum()),
        'defaulters': int((clients_df['outcome'] == 0).sum()),
        'avg_income': float(clients_df['income'].mean()),
        'avg_debt': float(clients_df['debt'].mean()),
        'generation_date': datetime.now().isoformat()
    }
    
    import json
    with open('data_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("   ✅ data_summary.json created")


if __name__ == "__main__":
    main()