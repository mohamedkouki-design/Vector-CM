"""
Ultimate Dataset Generator for Vector CM
Generates 2000+ realistic credit profiles for MENA region
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import json

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

print("="*70)
print("🚀 VECTOR CM - ULTIMATE DATASET GENERATOR")
print("="*70)

# ============================================================================
# TUNISIAN NAMES DATABASE
# ============================================================================

FIRST_NAMES_MALE = [
    'Mohamed', 'Ahmed', 'Ali', 'Youssef', 'Mehdi', 'Karim', 'Hamza', 'Bilel',
    'Sofiane', 'Tarek', 'Omar', 'Riadh', 'Anis', 'Fathi', 'Hichem', 'Nabil',
    'Sami', 'Walid', 'Zied', 'Aymen', 'Malek', 'Salim', 'Taoufik', 'Faouzi'
]

FIRST_NAMES_FEMALE = [
    'Fatima', 'Amal', 'Leila', 'Samira', 'Amira', 'Nadia', 'Salma', 'Ines',
    'Rania', 'Yasmine', 'Hiba', 'Nesrine', 'Sonia', 'Rim', 'Wafa', 'Hanen',
    'Sihem', 'Lamia', 'Ichrak', 'Meriem', 'Saida', 'Houda', 'Emna', 'Olfa'
]

LAST_NAMES = [
    'Ben Ali', 'Trabelsi', 'Bouazizi', 'Hamdi', 'Ayari', 'Mansour', 'Gharbi',
    'Jebali', 'Cherif', 'Slimani', 'Khiari', 'Dridi', 'Agrebi', 'Mejri',
    'Karoui', 'Besbes', 'Oueslati', 'Saidi', 'Daoud', 'Rebai', 'Essid',
    'Mabrouk', 'Labidi', 'Hajji', 'Fourati', 'Zouari', 'Tlili', 'Kraiem'
]

# ============================================================================
# FORMAL EMPLOYMENT TYPES (60% of dataset)
# ============================================================================

FORMAL_JOBS = {
    'bank_employee': {
        'description': 'Banking sector employee',
        'income_range': (2500, 4500),
        'stability_range': (0.92, 0.98),
        'debt_range': (0.20, 0.50),
        'typical_documents': ['pay_slip', 'employment_contract', 'bank_statement', 'id_card'],
        'repayment_probability': 0.91
    },
    'teacher': {
        'description': 'Public or private school teacher',
        'income_range': (2000, 3500),
        'stability_range': (0.88, 0.96),
        'debt_range': (0.25, 0.55),
        'typical_documents': ['pay_slip', 'employment_contract', 'id_card'],
        'repayment_probability': 0.89
    },
    'government_worker': {
        'description': 'Government employee or civil servant',
        'income_range': (2200, 4000),
        'stability_range': (0.93, 0.99),
        'debt_range': (0.20, 0.50),
        'typical_documents': ['pay_slip', 'civil_service_card', 'bank_statement', 'id_card'],
        'repayment_probability': 0.93
    },
    'corporate_employee': {
        'description': 'Private sector corporate employee',
        'income_range': (2800, 5500),
        'stability_range': (0.85, 0.95),
        'debt_range': (0.30, 0.60),
        'typical_documents': ['pay_slip', 'employment_contract', 'bank_statement', 'id_card'],
        'repayment_probability': 0.87
    },
    'nurse_healthcare': {
        'description': 'Healthcare professional',
        'income_range': (2300, 3800),
        'stability_range': (0.87, 0.94),
        'debt_range': (0.25, 0.55),
        'typical_documents': ['pay_slip', 'professional_license', 'bank_statement', 'id_card'],
        'repayment_probability': 0.90
    },
    'engineer': {
        'description': 'Engineering professional',
        'income_range': (3500, 6500),
        'stability_range': (0.88, 0.96),
        'debt_range': (0.30, 0.60),
        'typical_documents': ['pay_slip', 'employment_contract', 'bank_statement', 'id_card'],
        'repayment_probability': 0.88
    },
    'accountant': {
        'description': 'Accounting professional',
        'income_range': (2800, 4800),
        'stability_range': (0.86, 0.94),
        'debt_range': (0.28, 0.58),
        'typical_documents': ['pay_slip', 'employment_contract', 'bank_statement', 'id_card'],
        'repayment_probability': 0.89
    },
    'manager': {
        'description': 'Management position',
        'income_range': (4000, 7500),
        'stability_range': (0.84, 0.92),
        'debt_range': (0.35, 0.65),
        'typical_documents': ['pay_slip', 'employment_contract', 'bank_statement', 'id_card'],
        'repayment_probability': 0.86
    }
}

# ============================================================================
# INFORMAL EMPLOYMENT TYPES (30% of dataset)
# ============================================================================

INFORMAL_JOBS = {
    'market_vendor': {
        'description': 'Market vendor selling fresh produce or goods',
        'income_range': (800, 2500),
        'stability_range': (0.60, 0.85),
        'debt_range': (0.30, 0.70),
        'typical_documents': ['handwritten_ledger', 'supplier_receipt', 'market_license', 'id_card'],
        'repayment_probability': 0.74
    },
    'craftsman': {
        'description': 'Artisan or skilled tradesperson',
        'income_range': (1200, 3500),
        'stability_range': (0.65, 0.88),
        'debt_range': (0.25, 0.65),
        'typical_documents': ['invoice', 'material_receipt', 'client_reference', 'id_card'],
        'repayment_probability': 0.78
    },
    'gig_worker': {
        'description': 'Delivery driver, rideshare, or freelancer',
        'income_range': (600, 1800),
        'stability_range': (0.50, 0.75),
        'debt_range': (0.40, 0.80),
        'typical_documents': ['platform_statement', 'payment_proof', 'vehicle_license', 'id_card'],
        'repayment_probability': 0.68
    },
    'home_business': {
        'description': 'Home-based business (catering, sewing, tutoring)',
        'income_range': (900, 2800),
        'stability_range': (0.65, 0.85),
        'debt_range': (0.25, 0.60),
        'typical_documents': ['client_list', 'receipt', 'expense_log', 'id_card'],
        'repayment_probability': 0.76
    },
    'taxi_driver': {
        'description': 'Independent taxi or louage driver',
        'income_range': (1000, 2200),
        'stability_range': (0.60, 0.80),
        'debt_range': (0.35, 0.70),
        'typical_documents': ['vehicle_registration', 'daily_earnings_log', 'fuel_receipts', 'id_card'],
        'repayment_probability': 0.72
    },
    'street_vendor': {
        'description': 'Street vendor (food, accessories, goods)',
        'income_range': (500, 1500),
        'stability_range': (0.50, 0.70),
        'debt_range': (0.40, 0.85),
        'typical_documents': ['handwritten_ledger', 'supplier_receipt', 'id_card'],
        'repayment_probability': 0.65
    },
    'construction_worker': {
        'description': 'Construction or manual labor',
        'income_range': (700, 1900),
        'stability_range': (0.55, 0.75),
        'debt_range': (0.38, 0.75),
        'typical_documents': ['employer_reference', 'payment_record', 'id_card'],
        'repayment_probability': 0.70
    },
    'shop_owner': {
        'description': 'Small shop or store owner',
        'income_range': (1500, 3800),
        'stability_range': (0.68, 0.88),
        'debt_range': (0.28, 0.62),
        'typical_documents': ['sales_ledger', 'supplier_invoice', 'rent_receipt', 'id_card'],
        'repayment_probability': 0.77
    }
}

# ============================================================================
# LOAN SOURCES
# ============================================================================

LOAN_SOURCES = {
    'formal': [
        'amen_bank',
        'biat_bank', 
        'attijari_bank',
        'stb_bank',
        'bh_bank',
        'ubci_bank',
        'al_zitouna_bank'
    ],
    'informal': [
        'enda_microfinance',
        'atakaful_microfinance',
        'amssf_microfinance',
        'community_lending',
        'family_loan',
        'rotating_savings'
    ]
}

# ============================================================================
# TUNISIAN CITIES
# ============================================================================

TUNISIAN_CITIES = [
    'Tunis', 'Sfax', 'Sousse', 'Kairouan', 'Bizerte', 'Gabès', 'Ariana',
    'Gafsa', 'Monastir', 'Ben Arous', 'Kasserine', 'Médenine', 'Nabeul'
]

# ============================================================================
# DATA GENERATOR CLASS
# ============================================================================

class UltimateDataGenerator:
    """
    Generates ultra-realistic credit profiles for MENA region
    """
    
    def __init__(self):
        self.generated_clients = []
        self.generated_frauds = []
    
    def generate_client(self, client_id, category):
        """
        Generate a single client profile
        
        Args:
            client_id: Unique identifier
            category: 'formal_approved', 'informal_approved', or 'rejected'
        
        Returns:
            dict with complete client profile
        """
        
        # ====== STEP 1: Choose job type and employment ======
        if category == 'formal_approved':
            job_type = random.choice(list(FORMAL_JOBS.keys()))
            job_config = FORMAL_JOBS[job_type]
            employment_type = 'formal'
            loan_source = random.choice(LOAN_SOURCES['formal'])
            
        elif category == 'informal_approved':
            job_type = random.choice(list(INFORMAL_JOBS.keys()))
            job_config = INFORMAL_JOBS[job_type]
            employment_type = 'informal'
            loan_source = random.choice(LOAN_SOURCES['informal'])
            
        else:  # rejected
            # Rejected can be either formal or informal with terrible metrics
            if random.random() < 0.5:
                job_type = random.choice(list(FORMAL_JOBS.keys()))
                job_config = FORMAL_JOBS[job_type]
                employment_type = 'formal'
            else:
                job_type = random.choice(list(INFORMAL_JOBS.keys()))
                job_config = INFORMAL_JOBS[job_type]
                employment_type = 'informal'
            loan_source = 'none'
        
        # ====== STEP 2: Generate personal information ======
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)
        
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        location = random.choice(TUNISIAN_CITIES)
        age = random.randint(25, 60) if category != 'rejected' else random.randint(20, 65)
        
        # ====== STEP 3: Generate financial metrics ======
        if category == 'rejected':
            # Rejected have BAD metrics
            monthly_income = np.random.uniform(
                job_config['income_range'][0] * 0.6,
                job_config['income_range'][1] * 0.8
            )
            years_active = np.random.uniform(0.3, 4)
            debt_ratio = np.random.uniform(0.72, 0.95)
            income_stability = np.random.uniform(0.25, 0.58)
            payment_regularity = np.random.uniform(0.28, 0.62)
            
        else:
            # Approved have GOOD metrics
            monthly_income = np.random.uniform(*job_config['income_range'])
            years_active = np.random.uniform(1, 25)
            debt_ratio = np.random.uniform(*job_config['debt_range'])
            income_stability = np.random.uniform(*job_config['stability_range'])
            payment_regularity = np.random.uniform(0.72, 0.98)
        
        # Monthly expenses (typically 60-80% of income)
        expense_ratio = np.random.uniform(0.55, 0.82)
        monthly_expenses = monthly_income * expense_ratio
        
        # ====== STEP 4: Determine loan outcome ======
        if category == 'rejected':
            outcome = 'rejected'
            actual_outcome = 'N/A'
            loan_amount = 0
            approval_date = None
            
        else:
            outcome = 'approved'
            
            # Calculate repayment probability based on metrics
            base_prob = job_config['repayment_probability']
            
            # Adjust based on individual metrics
            metric_score = (
                (1 - debt_ratio) * 0.35 +
                income_stability * 0.30 +
                payment_regularity * 0.25 +
                min(years_active / 15, 1) * 0.10
            )
            
            # Final probability
            repay_prob = base_prob * 0.7 + metric_score * 0.3
            repay_prob = max(0.4, min(0.98, repay_prob))  # Clamp to realistic range
            
            # Determine if they actually repaid
            if random.random() < repay_prob:
                actual_outcome = 'repaid'
            else:
                actual_outcome = 'defaulted'
            
            # Loan amount (3-8x monthly income)
            loan_amount = monthly_income * np.random.uniform(3, 8)
            
            # Application and approval dates
            days_ago = np.random.randint(180, 1095)  # 6 months to 3 years ago
            approval_date = datetime.now() - timedelta(days=days_ago)
        
        # ====== STEP 5: Generate temporal snapshots (for approved) ======
        temporal_snapshots = []
        
        if outcome == 'approved':
            # T0: At application
            t0_risk = self._calculate_risk_score({
                'debt_ratio': debt_ratio,
                'income_stability': income_stability,
                'payment_regularity': payment_regularity
            })
            
            temporal_snapshots.append({
                'timestamp': 'T0_application',
                'date': approval_date.isoformat() if approval_date else None,
                'debt_ratio': round(debt_ratio, 3),
                'income_stability': round(income_stability, 3),
                'payment_regularity': round(payment_regularity, 3),
                'risk_score': round(t0_risk, 3),
                'status': 'pending'
            })
            
            # T1: 3 months after approval
            if actual_outcome == 'repaid':
                # Improving trajectory
                t1_debt = max(0.05, debt_ratio - np.random.uniform(0.05, 0.15))
                t1_stability = min(1.0, income_stability + np.random.uniform(0.02, 0.08))
                t1_regularity = min(1.0, payment_regularity + np.random.uniform(0.03, 0.1))
            else:
                # Declining trajectory
                t1_debt = min(0.95, debt_ratio + np.random.uniform(0.02, 0.1))
                t1_stability = max(0.2, income_stability - np.random.uniform(0.02, 0.08))
                t1_regularity = max(0.3, payment_regularity - np.random.uniform(0.05, 0.15))
            
            t1_risk = self._calculate_risk_score({
                'debt_ratio': t1_debt,
                'income_stability': t1_stability,
                'payment_regularity': t1_regularity
            })
            
            t1_date = approval_date + timedelta(days=90) if approval_date else None
            
            temporal_snapshots.append({
                'timestamp': 'T1_3months',
                'date': t1_date.isoformat() if t1_date else None,
                'debt_ratio': round(t1_debt, 3),
                'income_stability': round(t1_stability, 3),
                'payment_regularity': round(t1_regularity, 3),
                'risk_score': round(t1_risk, 3),
                'status': 'improving' if actual_outcome == 'repaid' else 'warning'
            })
            
            # T2: 6 months after approval
            if actual_outcome == 'repaid':
                t2_debt = max(0.05, t1_debt - np.random.uniform(0.05, 0.12))
                t2_stability = min(1.0, t1_stability + np.random.uniform(0.02, 0.05))
                t2_regularity = min(1.0, t1_regularity + np.random.uniform(0.02, 0.05))
            else:
                t2_debt = min(0.98, t1_debt + np.random.uniform(0.05, 0.15))
                t2_stability = max(0.15, t1_stability - np.random.uniform(0.03, 0.08))
                t2_regularity = max(0.25, t1_regularity - np.random.uniform(0.1, 0.2))
            
            t2_risk = self._calculate_risk_score({
                'debt_ratio': t2_debt,
                'income_stability': t2_stability,
                'payment_regularity': t2_regularity
            })
            
            t2_date = approval_date + timedelta(days=180) if approval_date else None
            
            temporal_snapshots.append({
                'timestamp': 'T2_6months',
                'date': t2_date.isoformat() if t2_date else None,
                'debt_ratio': round(t2_debt, 3),
                'income_stability': round(t2_stability, 3),
                'payment_regularity': round(t2_regularity, 3),
                'risk_score': round(t2_risk, 3),
                'status': 'good' if actual_outcome == 'repaid' else 'default'
            })
        
        # ====== STEP 6: Generate social network connections ======
        # For Trust Rings feature - 3-8 business connections per client
        num_connections = random.randint(3, 8)
        social_network = []
        
        for _ in range(num_connections):
            connection_type = random.choice([
                'supplier', 'customer', 'business_partner', 
                'family_business', 'peer_vendor'
            ])
            # Will be actual client IDs later
            social_network.append({
                'type': connection_type,
                'connection_id': f"CLIENT_{random.randint(0, 1999):04d}",
                'strength': round(random.uniform(0.3, 1.0), 2)
            })
        
        # ====== STEP 7: Compile complete profile ======
        application_date = datetime.now() - timedelta(days=np.random.randint(30, 1095))
        
        profile = {
            # Identity
            'client_id': client_id,
            'name': full_name,
            'age': age,
            'gender': gender,
            'location': location,
            
            # Employment
            'archetype': job_type,
            'job_description': job_config['description'],
            'employment_type': employment_type,
            'years_active': round(years_active, 1),
            
            # Financial metrics
            'monthly_income': round(monthly_income, 2),
            'monthly_expenses': round(monthly_expenses, 2),
            'debt_ratio': round(debt_ratio, 3),
            'income_stability': round(income_stability, 3),
            'payment_regularity': round(payment_regularity, 3),
            'savings_capacity': round((monthly_income - monthly_expenses) / monthly_income, 3),
            
            # Loan information
            'loan_source': loan_source,
            'loan_amount': round(loan_amount, 2),
            'outcome': outcome,
            'actual_outcome': actual_outcome,
            
            # Documents
            'documents': ','.join(job_config['typical_documents']),
            
            # Dates
            'application_date': application_date.isoformat(),
            'approval_date': approval_date.isoformat() if approval_date else None,
            
            # Advanced features
            'temporal_snapshots': json.dumps(temporal_snapshots),
            'social_network': json.dumps(social_network),
            
            # Risk scoring
            'initial_risk_score': round(self._calculate_risk_score({
                'debt_ratio': debt_ratio,
                'income_stability': income_stability,
                'payment_regularity': payment_regularity
            }), 3)
        }
        
        return profile
    
    def _calculate_risk_score(self, metrics):
        """Calculate risk score from metrics"""
        risk = (
            metrics['debt_ratio'] * 0.40 +
            (1 - metrics['income_stability']) * 0.30 +
            (1 - metrics['payment_regularity']) * 0.30
        )
        return min(1.0, max(0.0, risk))
    
    def generate_fraud_pattern(self, fraud_id):
        """Generate sophisticated fraud pattern"""
        
        fraud_types = [
            'synthetic_identity',
            'income_inflation',
            'document_forgery',
            'identity_theft',
            'duplicate_application',
            'fake_business',
            'shell_company',
            'first_party_fraud'
        ]
        
        fraud_type = random.choice(fraud_types)
        
        # Generate suspicious profile
        job_type = random.choice(list(INFORMAL_JOBS.keys()))
        
        # Frauds have RED FLAGS
        profile = {
            'fraud_id': fraud_id,
            'fraud_type': fraud_type,
            'name': f"{random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)} {random.choice(LAST_NAMES)}",
            'archetype': job_type,
            'employment_type': 'informal',
            'years_active': round(np.random.uniform(0.2, 2.5), 1),  # Very short history
            'monthly_income': round(np.random.uniform(4000, 12000), 2),  # Unrealistically high
            'debt_ratio': round(np.random.uniform(0.82, 0.98), 3),  # Very high debt
            'income_stability': round(np.random.uniform(0.15, 0.42), 3),  # Very unstable
            'payment_regularity': round(np.random.uniform(0.22, 0.53), 3),  # Poor history
            'loan_source': 'attempted_fraud',
            'documents': 'forged_invoice.jpg,suspicious_id.jpg,fake_ledger.jpg',
            'detected_date': (datetime.now() - timedelta(days=np.random.randint(1, 365))).isoformat(),
            'fraud_indicators': self._generate_fraud_indicators(fraud_type),
            'fraud_narrative': self._generate_fraud_narrative(fraud_type)
        }
        
        return profile
    
    def _generate_fraud_indicators(self, fraud_type):
        """Generate specific fraud indicators"""
        indicators = {
            'synthetic_identity': [
                'SSN_mismatch', 'recent_credit_file_creation',
                'multiple_addresses', 'inconsistent_employment_history'
            ],
            'income_inflation': [
                'income_3x_industry_average', 'bank_statement_mismatch',
                'employer_verification_failed', 'tax_records_inconsistent'
            ],
            'document_forgery': [
                'template_match_known_forgery', 'metadata_recent_creation',
                'font_inconsistencies', 'digital_manipulation_detected'
            ],
            'identity_theft': [
                'deceased_person_ssn', 'biometric_mismatch',
                'address_not_associated_with_identity', 'velocity_check_failed'
            ],
            'duplicate_application': [
                'same_device_fingerprint', 'similar_application_pattern',
                'identical_employment_details', 'sequential_submission_times'
            ],
            'fake_business': [
                'no_online_presence', 'residential_business_address',
                'zero_customer_reviews', 'business_license_invalid'
            ]
        }
        
        return ','.join(indicators.get(fraud_type, ['suspicious_activity']))
    
    def _generate_fraud_narrative(self, fraud_type):
        """Generate realistic fraud narrative"""
        narratives = {
            'synthetic_identity': 
                'Applicant profile combines elements from multiple real identities. '
                'Credit file created within last 6 months. Employment history cannot be verified. '
                'Address associated with multiple unrelated identities.',
            
            'income_inflation':
                'Reported income 3.2x above industry average for stated occupation. '
                'Bank statements show significantly lower deposit patterns. '
                'Employer contacted - position does not exist at stated salary level.',
            
            'document_forgery':
                'Submitted invoice matches template used in 12 previous fraud cases. '
                'Document metadata shows creation date 3 days before submission. '
                'Font analysis reveals digital manipulation. Vendor contact failed.',
            
            'identity_theft':
                'ID card number belongs to deceased individual (died 2 years ago). '
                'Biometric verification failed - photo does not match database records. '
                'Address has no connection to claimed identity in public records.',
            
            'duplicate_application':
                'Same applicant submitted 4 applications in 2 months with minor variations. '
                'Device fingerprint matches across all submissions. '
                'Email addresses follow sequential pattern. IP geolocation inconsistent.',
            
            'fake_business':
                'Business address is residential property. Zero online presence or reviews. '
                'Business license number does not exist in registry. '
                'Stated suppliers deny any business relationship.',
            
            'shell_company':
                'Company registered 2 weeks before loan application. '
                'No employees, no equipment, no business activity. '
                'Sole purpose appears to be obtaining credit.',
            
            'first_party_fraud':
                'Applicant deliberately misrepresented financial situation. '
                'Claimed employment that ended 8 months ago. '
                'Used family member\'s income documents without authorization.'
        }
        
        return narratives.get(fraud_type, 'Suspicious activity pattern detected through vector similarity analysis.')
    
    def generate_complete_dataset(self):
        """Generate complete dataset with all profiles"""
        
        print("\n📊 Generating client profiles...")
        print("-" * 70)
        
        clients = []
        
        # 1200 formal approved (60%)
        print("  [1/3] Generating 1200 formal sector clients...")
        for i in range(200):
            client = self.generate_client(f'CLIENT_{i:04d}', 'formal_approved')
            clients.append(client)
            if (i + 1) % 200 == 0:
                print(f"        Generated {i + 1}/1200 formal clients...")
        
        # 600 informal approved (30%)
        print("\n  [2/3] Generating 600 informal sector clients...")
        for i in range(200, 300):
            client = self.generate_client(f'CLIENT_{i:04d}', 'informal_approved')
            clients.append(client)
            if (i + 1 - 200) % 100 == 0:
                print(f"        Generated {i + 1 - 200}/600 informal clients...")
        
        # 200 rejected (10%)
        print("\n  [3/3] Generating 200 rejected applications...")
        for i in range(300, 320):
            client = self.generate_client(f'CLIENT_{i:04d}', 'rejected')
            clients.append(client)
            if (i + 1 - 300) % 50 == 0:
                print(f"        Generated {i + 1 - 300}/200 rejected clients...")
        
        # Shuffle for realism
        random.shuffle(clients)
        self.generated_clients = clients
        
        # Generate fraud patterns
        print("\n🚨 Generating fraud patterns...")
        print("-" * 70)
        
        frauds = []
        for i in range(200):
            fraud = self.generate_fraud_pattern(f'FRAUD_{i:04d}')
            frauds.append(fraud)
            if (i + 1) % 50 == 0:
                print(f"  Generated {i + 1}/200 fraud patterns...")
        
        self.generated_frauds = frauds
        
        return clients, frauds

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Initialize generator
    generator = UltimateDataGenerator()
    
    # Generate complete dataset
    clients, frauds = generator.generate_complete_dataset()
    
    # Save to CSV
    print("\n💾 Saving datasets...")
    print("-" * 70)
    
    clients_df = pd.DataFrame(clients)
    clients_df.to_csv('synthetic_clients_ultimate.csv', index=False)
    print(f"  ✅ Saved clients to: synthetic_clients_ultimate.csv")
    
    frauds_df = pd.DataFrame(frauds)
    frauds_df.to_csv('synthetic_frauds_ultimate.csv', index=False)
    print(f"  ✅ Saved frauds to: synthetic_frauds_ultimate.csv")
    
    # Print comprehensive statistics
    print("\n" + "="*70)
    print("📈 DATASET STATISTICS")
    print("="*70)
    
    print(f"\n📊 CLIENT DISTRIBUTION:")
    print(f"  Total clients: {len(clients)}")
    
    formal_approved = sum(1 for c in clients if c['employment_type'] == 'formal' and c['outcome'] == 'approved')
    informal_approved = sum(1 for c in clients if c['employment_type'] == 'informal' and c['outcome'] == 'approved')
    rejected = sum(1 for c in clients if c['outcome'] == 'rejected')
    
    print(f"  Formal sector (approved): {formal_approved} ({formal_approved/len(clients)*100:.1f}%)")
    print(f"  Informal sector (approved): {informal_approved} ({informal_approved/len(clients)*100:.1f}%)")
    print(f"  Rejected: {rejected} ({rejected/len(clients)*100:.1f}%)")
    
    print(f"\n💰 LOAN OUTCOMES (Approved clients only):")
    approved = [c for c in clients if c['outcome'] == 'approved']
    repaid = sum(1 for c in approved if c['actual_outcome'] == 'repaid')
    defaulted = sum(1 for c in approved if c['actual_outcome'] == 'defaulted')
    
    print(f"  Total approved loans: {len(approved)}")
    print(f"  Successfully repaid: {repaid} ({repaid/len(approved)*100:.1f}%)")
    print(f"  Defaulted: {defaulted} ({defaulted/len(approved)*100:.1f}%)")
    
    print(f"\n🏦 LOAN SOURCES:")
    loan_source_counts = {}
    for c in clients:
        source = c['loan_source']
        loan_source_counts[source] = loan_source_counts.get(source, 0) + 1
    
    for source, count in sorted(loan_source_counts.items(), key=lambda x: x[1], reverse=True):
        if source != 'none':
            print(f"  {source}: {count}")
    
    print(f"\n🚨 FRAUD PATTERNS:")
    print(f"  Total fraud cases: {len(frauds)}")
    
    fraud_type_counts = {}
    for f in frauds:
        ftype = f['fraud_type']
        fraud_type_counts[ftype] = fraud_type_counts.get(ftype, 0) + 1
    
    for ftype, count in sorted(fraud_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ftype}: {count}")
    
    print(f"\n📍 GEOGRAPHIC DISTRIBUTION:")
    location_counts = {}
    for c in clients:
        loc = c['location']
        location_counts[loc] = location_counts.get(loc, 0) + 1
    
    for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {loc}: {count}")
    
    print(f"\n💼 TOP JOB ARCHETYPES:")
    job_counts = {}
    for c in clients:
        job = c['archetype']
        job_counts[job] = job_counts.get(job, 0) + 1
    
    for job, count in sorted(job_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"  {job}: {count}")
    
    print("\n" + "="*70)
    print("✅ ULTIMATE DATASET GENERATION COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run: python ../populate_qdrant.py")
    print("  2. Update collection vector dimensions if using multimodal")
    print("  3. Test search with new diverse dataset")