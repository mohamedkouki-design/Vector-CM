import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from qdrant_manager import CreditMemory
from utils import find_success_twin, calculate_improvement_path
import numpy as np

# Initialize
if 'memory' not in st.session_state:
    st.session_state.memory = CreditMemory()

memory = st.session_state.memory

# Page config
st.set_page_config(page_title="Vector Credit Memory", layout="wide", page_icon="🧠")

# Custom CSS
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .metric-card { padding: 20px; border-radius: 10px; background: #f0f2f6; }
    .success-box { padding: 15px; background: #d4edda; border-left: 5px solid #28a745; border-radius: 5px; }
    .warning-box { padding: 15px; background: #fff3cd; border-left: 5px solid #ffc107; border-radius: 5px; }
    .danger-box { padding: 15px; background: #f8d7da; border-left: 5px solid #dc3545; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="big-font">🧠 Vector Credit Memory</p>', unsafe_allow_html=True)
st.markdown("**Self-Evolving Multimodal Credit Intelligence for MENA Informal Economy**")

# Sidebar - Dashboard selection
dashboard = st.sidebar.radio(
    "Select Dashboard",
    ["🏠 Overview", "👤 Client Portal", "⚙️ Admin Command Center"]
)

#############################################
# DEMO SCENARIOS DATA
#############################################
DEMO_SCENARIOS = {
    "Manual Entry": None,
    "✅ Strong Profile (Likely Approved)": {
        'income': 1800,
        'expenses': 1000,
        'debt': 500,
        'age': 42,
        'seniority_months': 60,
        'payment_consistency': 0.92,
        'loan_amount': 2000,
        'employment_type': 'formal',
        'story': "Established electrician with 5 years in business, low debt, high consistency"
    },
    "⚠️ Borderline Profile (Needs Improvement)": {
        'income': 1200,
        'expenses': 900,
        'debt': 2000,
        'age': 35,
        'seniority_months': 24,
        'payment_consistency': 0.75,
        'loan_amount': 2500,
        'employment_type': 'mixed',
        'story': "Freelance designer with moderate income, manageable debt, 2 years experience"
    },
    "❌ High-Risk Profile (Likely Rejected)": {
        'income': 600,
        'expenses': 550,
        'debt': 3000,
        'age': 28,
        'seniority_months': 8,
        'payment_consistency': 0.65,
        'loan_amount': 3000,
        'employment_type': 'informal',
        'story': "Market vendor with high debt-to-income ratio, short business history"
    },
    "🚨 Fraud Attempt": {
        'income': 8000,
        'expenses': 1500,
        'debt': 100,
        'age': 22,
        'seniority_months': 2,
        'payment_consistency': 1.0,
        'loan_amount': 12000,
        'employment_type': 'informal',
        'story': "Suspicious: Unrealistic income for informal worker, perfect consistency, minimal debt"
    }
}

#############################################
# OVERVIEW DASHBOARD
#############################################
if dashboard == "🏠 Overview":
    st.header("System Overview")
    
    # Load data for metrics
    try:
        df = pd.read_csv('synthetic_clients.csv')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cases", f"{len(df)}", delta="Historical memory")
        with col2:
            good_count = (df['outcome'] == 1).sum()
            st.metric("Good Payers", f"{good_count}", delta=f"{good_count/len(df)*100:.0f}%")
        with col3:
            bad_count = (df['outcome'] == 0).sum()
            st.metric("Defaulters", f"{bad_count}", delta=f"{bad_count/len(df)*100:.0f}%")
        with col4:
            try:
                fraud_df = pd.read_csv('synthetic_frauds.csv')
                st.metric("Fraud Patterns", f"{len(fraud_df)}", delta="Known cases")
            except:
                st.metric("Fraud Patterns", "100", delta="Known cases")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Outcome Distribution")
            outcome_counts = df['outcome'].value_counts()
            fig = px.pie(
                values=outcome_counts.values,
                names=['Defaulted', 'Repaid'],
                title="Historical Repayment Outcomes",
                color_discrete_sequence=['#ff6b6b', '#51cf66']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Income vs Debt Distribution")
            fig = px.scatter(
                df,
                x='income',
                y='debt',
                color='outcome',
                size='loan_amount',
                hover_data=['client_id', 'payment_consistency'],
                color_discrete_map={0: '#ff6b6b', 1: '#51cf66'},
                labels={'outcome': 'Outcome', 'income': 'Monthly Income ($)', 'debt': 'Total Debt ($)'}
            )
            fig.update_traces(marker=dict(opacity=0.6))
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Key Insights")
        
        good_payers = df[df['outcome'] == 1]
        defaulters = df[df['outcome'] == 0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Avg Income (Good Payers)",
                f"${good_payers['income'].mean():.0f}",
                delta=f"+${good_payers['income'].mean() - defaulters['income'].mean():.0f} vs defaulters"
            )
        
        with col2:
            st.metric(
                "Avg Debt (Good Payers)",
                f"${good_payers['debt'].mean():.0f}",
                delta=f"-${defaulters['debt'].mean() - good_payers['debt'].mean():.0f} vs defaulters",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Avg Payment Consistency",
                f"{good_payers['payment_consistency'].mean():.0%}",
                delta=f"+{(good_payers['payment_consistency'].mean() - defaulters['payment_consistency'].mean()):.0%}"
            )
    
    except FileNotFoundError:
        st.error("⚠️ Data files not found. Please run `python demo_data.py` first!")

#############################################
# CLIENT PORTAL
#############################################
elif dashboard == "👤 Client Portal":
    st.header("Credit Application Portal")
    st.markdown("### Step 1: Choose Application Type")
    
    # Demo scenario selector
    scenario_choice = st.selectbox(
        "Select a scenario to test, or enter manually",
        list(DEMO_SCENARIOS.keys()),
        help="Try different profiles to see how the system works"
    )
    
    if scenario_choice != "Manual Entry":
        scenario = DEMO_SCENARIOS[scenario_choice]
        st.info(f"**Scenario:** {scenario['story']}")
    
    st.markdown("### Step 2: Enter Financial Information")
    
    col1, col2 = st.columns(2)
    
    # Get values from scenario or use defaults
    if scenario_choice != "Manual Entry":
        scenario = DEMO_SCENARIOS[scenario_choice]
        default_income = scenario['income']
        default_expenses = scenario['expenses']
        default_debt = scenario['debt']
        default_age = scenario['age']
        default_seniority = scenario['seniority_months']
        default_consistency = scenario['payment_consistency']
        default_loan = scenario['loan_amount']
        default_employment = scenario['employment_type']
    else:
        default_income = 1200
        default_expenses = 900
        default_debt = 1500
        default_age = 35
        default_seniority = 24
        default_consistency = 0.7
        default_loan = 2000
        default_employment = 'informal'
    
    with col1:
        income = st.number_input(
            "Monthly Income ($)",
            min_value=100,
            max_value=15000,
            value=default_income,
            help="Your average monthly income from your business"
        )
        expenses = st.number_input(
            "Monthly Expenses ($)",
            min_value=50,
            max_value=15000,
            value=default_expenses,
            help="Your average monthly business and personal expenses"
        )
        debt = st.number_input(
            "Current Total Debt ($)",
            min_value=0,
            max_value=50000,
            value=default_debt,
            help="All outstanding debts combined"
        )
        age = st.number_input(
            "Your Age",
            min_value=18,
            max_value=100,
            value=default_age
        )
    
    with col2:
        seniority = st.number_input(
            "Business Seniority (months)",
            min_value=1,
            max_value=240,
            value=default_seniority,
            help="How long you've been operating your business"
        )
        payment_consistency = st.slider(
            "Payment Consistency",
            0.0,
            1.0,
            default_consistency,
            help="How consistently you pay bills on time (0=never, 1=always)"
        )
        loan_amount = st.number_input(
            "Requested Loan Amount ($)",
            min_value=100,
            max_value=20000,
            value=default_loan,
            help="How much credit you're applying for"
        )
        employment_type = st.selectbox(
            "Employment Type",
            ["informal", "mixed", "formal"],
            index=["informal", "mixed", "formal"].index(default_employment),
            help="Informal=no contracts, Mixed=some formal income, Formal=salaried"
        )
    
    st.markdown("### Step 3: Analyze Your Profile")
    
    if st.button("🔍 Submit Application", type="primary", use_container_width=True):
        with st.spinner("Analyzing your profile against 1,900 historical cases..."):
            # Create client data
            new_client = pd.Series({
                'client_id': 'NEW_CLIENT',
                'income': income,
                'expenses': expenses,
                'debt': debt,
                'age': age,
                'seniority_months': seniority,
                'payment_consistency': payment_consistency,
                'loan_amount': loan_amount,
                'employment_type': employment_type,
                'outcome': -1  # Unknown
            })
            
            # STEP 1: Check fraud first
            is_fraud, fraud_score = memory.check_fraud(new_client)
            
            if is_fraud:
                st.markdown("---")
                st.markdown('<div class="danger-box">', unsafe_allow_html=True)
                st.markdown(f"### 🚨 Fraud Alert")
                st.markdown(f"""
                Your profile matches known fraud patterns with **{fraud_score:.0%} similarity**.
                
                **Common fraud indicators detected:**
                - Unrealistic income for informal sector
                - Perfect payment consistency (too good to be true)
                - Minimal debt despite high income claims
                - Very short business history with large loan request
                
                **Next Steps:**
                - Application automatically flagged for manual review
                - Additional documentation required
                - Identity verification needed
                """)
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            
            # STEP 2: Find similar clients
            similar = memory.find_similar_clients(new_client, top_k=20)
            
            if not similar:
                st.error("Unable to find similar cases. Please check your Qdrant connection.")
                st.stop()
            
            # STEP 3: Analyze outcomes
            outcomes = [s.payload['outcome'] for s in similar]
            good_payers = sum(outcomes)
            defaulters = len(outcomes) - good_payers
            approval_likelihood = good_payers / len(outcomes)
            
            # STEP 4: Show results based on likelihood
            st.markdown("---")
            st.markdown("## 📊 Application Results")
            
            # Decision box
            if approval_likelihood >= 0.7:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### ✅ Strong Approval Likelihood: {approval_likelihood:.0%}")
                st.markdown(f"""
                Based on similarity to {len(similar)} historical cases:
                - **{good_payers} similar clients** successfully repaid their loans
                - **{defaulters} similar clients** defaulted
                
                **Recommendation:** Approve with standard terms
                """)
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif approval_likelihood >= 0.4:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.markdown(f"### ⚠️ Borderline Profile: {approval_likelihood:.0%} Approval Likelihood")
                st.markdown(f"""
                Based on similarity to {len(similar)} historical cases:
                - **{good_payers} similar clients** successfully repaid
                - **{defaulters} similar clients** defaulted
                
                **Recommendation:** Review improvements below to increase approval chances
                """)
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                st.markdown('<div class="danger-box">', unsafe_allow_html=True)
                st.markdown(f"### ❌ Low Approval Likelihood: {approval_likelihood:.0%}")
                st.markdown(f"""
                Based on similarity to {len(similar)} historical cases:
                - **{good_payers} similar clients** successfully repaid
                - **{defaulters} similar clients** defaulted
                
                **Recommendation:** Focus on improvements below before reapplying
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Approval Likelihood", f"{approval_likelihood:.0%}")
            with col2:
                st.metric("Similar Good Payers", good_payers, delta="Positive signals")
            with col3:
                st.metric("Similar Defaulters", defaulters, delta="Risk signals", delta_color="inverse")
            
            # Similar cases table
            st.markdown("### 👥 Your Top 5 Financial Twins")
            st.markdown("*These are the most similar historical cases in our database*")
            
            similar_data = []
            for s in similar[:5]:
                similar_data.append({
                    'Similarity': f"{s.score:.0%}",
                    'Income': f"${s.payload['income']:.0f}",
                    'Debt': f"${s.payload['debt']:.0f}",
                    'Seniority': f"{s.payload['seniority_months']} mo",
                    'Consistency': f"{s.payload['payment_consistency']:.0%}",
                    'Outcome': '✅ Repaid' if s.payload['outcome'] == 1 else '❌ Defaulted'
                })
            
            st.dataframe(pd.DataFrame(similar_data), use_container_width=True, hide_index=True)
            
            # SUCCESS TWIN (only if approval < 70%)
            if approval_likelihood < 0.7:
                st.markdown("---")
                st.markdown("## 🌟 Your Success Twin - Path to Approval")
                
                success_twin = find_success_twin(memory, new_client, min_similarity=0.5)
                
                if success_twin:
                    st.success(f"✨ We found a client who started **{success_twin.score:.0%} similar** to you and successfully repaid!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 👤 Your Current Profile")
                        st.write(f"💰 Income: **${income:,.0f}**/month")
                        st.write(f"💳 Debt: **${debt:,.0f}**")
                        st.write(f"📅 Seniority: **{seniority} months**")
                        st.write(f"✅ Consistency: **{payment_consistency:.0%}**")
                        st.write(f"📊 Approval: **{approval_likelihood:.0%}**")
                    
                    with col2:
                        twin_approval = 0.85  # Assumption for success twin
                        st.markdown(f"#### ⭐ Success Twin Profile")
                        st.write(f"💰 Income: **${success_twin.payload['income']:,.0f}**/month")
                        st.write(f"💳 Debt: **${success_twin.payload['debt']:,.0f}**")
                        st.write(f"📅 Seniority: **{success_twin.payload['seniority_months']} months**")
                        st.write(f"✅ Consistency: **{success_twin.payload['payment_consistency']:.0%}**")
                        st.write(f"📊 Result: **✅ Approved & Repaid**")
                    
                    # Improvement path
                    improvements = calculate_improvement_path(new_client, success_twin.payload)
                    
                    if improvements:
                        st.markdown("### 🎯 Your Personalized Improvement Plan")
                        st.markdown("*Follow these steps to match your Success Twin's profile:*")
                        
                        for i, imp in enumerate(improvements, 1):
                            with st.expander(f"Step {i}: Improve {imp['factor']}", expanded=True):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown("**Current**")
                                    st.markdown(f"### {imp['current']}")
                                with col2:
                                    st.markdown("**Target**")
                                    st.markdown(f"### {imp['target']}")
                                with col3:
                                    st.markdown("**Action Required**")
                                    st.markdown(f"**{imp['action']}**")
                    else:
                        st.info("🎉 You're already very close to your Success Twin's profile! Small improvements will help.")
                else:
                    st.warning("⚠️ No close success twin found with minimum 50% similarity. Try improving your overall financial health.")

#############################################
# ADMIN COMMAND CENTER
#############################################
elif dashboard == "⚙️ Admin Command Center":
    st.header("Admin Command Center")
    
    tab1, tab2 = st.tabs(["📊 Vector Space Explorer", "🔮 What-If Counterfactual Engine"])
    
    with tab1:
        st.markdown("### Vector Space Visualization")
        
        try:
            df = pd.read_csv('synthetic_clients.csv')
            
            # Simple 2D projection
            df['income_norm'] = df['income'] / 5000
            df['debt_norm'] = df['debt'] / 10000
            
            fig = go.Figure()
            
            # Good payers
            good = df[df['outcome'] == 1]
            fig.add_trace(go.Scatter(
                x=good['income_norm'],
                y=good['debt_norm'],
                mode='markers',
                name='Good Payers',
                marker=dict(color='#51cf66', size=8, opacity=0.6),
                text=good['client_id'],
                hovertemplate='<b>%{text}</b><br>Income: %{x:.2f}<br>Debt: %{y:.2f}<extra></extra>'
            ))
            
            # Defaulters
            bad = df[df['outcome'] == 0]
            fig.add_trace(go.Scatter(
                x=bad['income_norm'],
                y=bad['debt_norm'],
                mode='markers',
                name='Defaulters',
                marker=dict(color='#ff6b6b', size=8, opacity=0.6),
                text=bad['client_id'],
                hovertemplate='<b>%{text}</b><br>Income: %{x:.2f}<br>Debt: %{y:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Client Vector Space (Income vs Debt)",
                xaxis_title="Normalized Income",
                yaxis_title="Normalized Debt",
                height=600,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            st.markdown("### 📈 System Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_income_good = df[df['outcome'] == 1]['income'].mean()
                st.metric("Avg Income (Good Payers)", f"${avg_income_good:.0f}")
            
            with col2:
                avg_debt_good = df[df['outcome'] == 1]['debt'].mean()
                st.metric("Avg Debt (Good Payers)", f"${avg_debt_good:.0f}")
            
            with col3:
                avg_consistency = df[df['outcome'] == 1]['payment_consistency'].mean()
                st.metric("Avg Payment Consistency", f"{avg_consistency:.2%}")
        
        except FileNotFoundError:
            st.error("Data files not found. Run `python demo_data.py` first.")
    
    with tab2:
        st.markdown("### What-If Counterfactual Engine")
        st.markdown("*Modify client variables to see how their approval likelihood changes*")
        
        try:
            df = pd.read_csv('synthetic_clients.csv')
            
            # Select client
            client_ids = df['client_id'].tolist()
            selected_id = st.selectbox("Select a client to analyze", client_ids, index=0)
            
            selected_client = df[df['client_id'] == selected_id].iloc[0]
            
            st.markdown("#### Original Profile")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Income", f"${selected_client['income']:.0f}")
            with col2:
                st.metric("Debt", f"${selected_client['debt']:.0f}")
            with col3:
                st.metric("Seniority", f"{selected_client['seniority_months']} mo")
            with col4:
                outcome_text = "✅ Repaid" if selected_client['outcome'] == 1 else "❌ Defaulted"
                st.metric("Actual Outcome", outcome_text)
            
            st.markdown("---")
            st.markdown("#### Modify Variables")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_income = st.slider(
                    "Adjust Income ($)",
                    min_value=int(selected_client['income'] * 0.5),
                    max_value=int(selected_client['income'] * 2),
                    value=int(selected_client['income']),
                    step=100
                )
                
                new_debt = st.slider(
                    "Adjust Debt ($)",
                    min_value=0,
                    max_value=int(selected_client['debt'] * 2),
                    value=int(selected_client['debt']),
                    step=100
                )
            
            with col2:
                new_seniority = st.slider(
                    "Adjust Business Seniority (months)",
                    min_value=1,
                    max_value=120,
                    value=int(selected_client['seniority_months'])
                )
                
                new_consistency = st.slider(
                    "Adjust Payment Consistency",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(selected_client['payment_consistency']),
                    step=0.05
                )
            
            if st.button("🔄 Recalculate Approval Likelihood", type="primary"):
                with st.spinner("Re-querying vector space..."):
                    # Get original neighbors
                    original_similar = memory.find_similar_clients(selected_client, top_k=20)
                    original_outcomes = [s.payload['outcome'] for s in original_similar]
                    original_approval = sum(original_outcomes) / len(original_outcomes)
                    
                    # Create modified client
                    modified_client = selected_client.copy()
                    modified_client['income'] = new_income
                    modified_client['debt'] = new_debt
                    modified_client['seniority_months'] = new_seniority
                    modified_client['payment_consistency'] = new_consistency
                    
                    # Get modified neighbors
                    modified_similar = memory.find_similar_clients(modified_client, top_k=20)
                    modified_outcomes = [s.payload['outcome'] for s in modified_similar]
                    modified_approval = sum(modified_outcomes) / len(modified_outcomes)
                    
                    # Show impact
                    st.markdown("---")
                    st.markdown("### 📊 Impact Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Original Approval", f"{original_approval:.0%}")
                    
                    with col2:
                        delta_value = modified_approval - original_approval
                        st.metric(
                            "Modified Approval",
                            f"{modified_approval:.0%}",
                            delta=f"{delta_value:+.0%}"
                        )
                    
                    with col3:
                        improvement = modified_approval - original_approval
                        if improvement > 0.15:
                            st.success("🎯 Significant Improvement!")
                        elif improvement > 0:
                            st.info("📈 Slight Improvement")
                        elif improvement < -0.15:
                            st.error("📉 Position Worsened")
                        else:
                            st.warning("➡️ Minimal Change")
                    
                    # Visualization
                    st.markdown("### 📊 Cluster Shift Analysis")
                    
                    comparison_df = pd.DataFrame([
                        {
                            'Scenario': 'Original',
                            'Good Payers': sum(original_outcomes),
                            'Defaulters': len(original_outcomes) - sum(original_outcomes)
                        },
                        {
                            'Scenario': 'Modified',
                            'Good Payers': sum(modified_outcomes),
                            'Defaulters': len(modified_outcomes) - sum(modified_outcomes)
                        }
                    ])
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Good Payers',
                            x=comparison_df['Scenario'],
                            y=comparison_df['Good Payers'],
                            marker_color='#51cf66',
                            text=comparison_df['Good Payers'],
                            textposition='auto'
                        ),
                        go.Bar(
                            name='Defaulters',
                            x=comparison_df['Scenario'],
                            y=comparison_df['Defaulters'],
                            marker_color='#ff6b6b',
                            text=comparison_df['Defaulters'],
                            textposition='auto'
                        )
                    ])
                    
                    fig.update_layout(
                        barmode='stack',
                        title="Nearest Neighbors Composition (20 neighbors)",
                        yaxis_title="Count",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Recommendation
                    if modified_approval > original_approval + 0.1:
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown(f"""
                        ### ✨ Path to Approval Identified!
                        
                        By making these changes:
                        - Income: ${selected_client['income']:.0f} → ${new_income:.0f} ({new_income - selected_client['income']:+.0f})
                        - Debt: ${selected_client['debt']:.0f} → ${new_debt:.0f} ({new_debt - selected_client['debt']:+.0f})
                        - Seniority: {selected_client['seniority_months']} → {new_seniority} months ({new_seniority - selected_client['seniority_months']:+} months)
                        - Consistency: {selected_client['payment_consistency']:.0%} → {new_consistency:.0%}
                        
                        **Approval likelihood improves from {original_approval:.0%} to {modified_approval:.0%}**
                        
                        This client would move closer to successful repayment patterns in the vector space.
                        """)
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif modified_approval < original_approval - 0.1:
                        st.warning(f"⚠️ These changes would worsen the approval likelihood from {original_approval:.0%} to {modified_approval:.0%}")
                    else:
                        st.info("These changes have minimal impact on approval likelihood. Try larger adjustments.")
        
        except FileNotFoundError:
            st.error("Data files not found.")
