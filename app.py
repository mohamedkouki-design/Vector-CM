import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from qdrant_manager import CreditMemory
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
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="big-font">🧠 Vector Credit Memory</p>', unsafe_allow_html=True)
st.markdown("**Self-Evolving Multimodal Credit Intelligence**")

# Sidebar - Dashboard selection
dashboard = st.sidebar.radio(
    "Select Dashboard",
    ["🏠 Overview", "👤 Client Portal", "⚙️ Admin Command Center"]
)

#############################################
# OVERVIEW DASHBOARD
#############################################
if dashboard == "🏠 Overview":
    st.header("System Overview")
    
    # Load data for metrics
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
            st.metric("Fraud Patterns", "0", delta="Not loaded")
    st.markdown("---")
    # Load data for visualization
    df = pd.read_csv('synthetic_clients.csv')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Outcome Distribution")
        fig = px.pie(
            df, 
            names='outcome',
            title="Repaid vs Defaulted",
            color='outcome',
            color_discrete_map={0: '#ff6b6b', 1: '#51cf66'}
        )
        fig.update_traces(labels=['Defaulted', 'Repaid'])
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
            color_discrete_map={0: '#ff6b6b', 1: '#51cf66'}
        )
        st.plotly_chart(fig, use_container_width=True)

#############################################
# CLIENT PORTAL
#############################################
elif dashboard == "👤 Client Portal":
    st.header("Client Application Portal")
    
    st.markdown("### Enter Your Financial Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        income = st.number_input("Monthly Income ($)", min_value=100, max_value=10000, value=800)
        expenses = st.number_input("Monthly Expenses ($)", min_value=50, max_value=10000, value=600)
        debt = st.number_input("Current Debt ($)", min_value=0, max_value=20000, value=1000)
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
    
    with col2:
        seniority = st.number_input("Business Seniority (months)", min_value=1, max_value=240, value=24)
        payment_consistency = st.slider("Payment Consistency (self-reported)", 0.0, 1.0, 0.7)
        loan_amount = st.number_input("Requested Loan Amount ($)", min_value=100, max_value=10000, value=2000)
        employment_type = st.selectbox("Employment Type", ["informal", "formal", "mixed"])
    
    if st.button("🔍 Analyze My Profile", type="primary"):
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
        
        # Check fraud first
        is_fraud, fraud_score = memory.check_fraud(new_client)
        
        if is_fraud:
            st.error(f"⚠️ **Fraud Alert**: Your profile matches known fraud patterns (similarity: {fraud_score:.2%})")
            st.stop()
        
        # Find similar clients
        similar = memory.find_similar_clients(new_client, top_k=10)
        
        
        # Analyze outcomes
        outcomes = [s.payload['outcome'] for s in similar]
        good_payers = sum(outcomes)
        defaulters = len(outcomes) - good_payers
        
        approval_likelihood = good_payers / len(outcomes)
        
        st.markdown("---")
        st.subheader("📊 Your Profile Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Approval Likelihood", f"{approval_likelihood:.0%}")
        with col2:
            st.metric("Similar Good Payers", good_payers)
        with col3:
            st.metric("Similar Defaulters", defaulters)
        
        # Show decision
        if approval_likelihood >= 0.6:
            st.success(f"✅ **Likely to be Approved** - {good_payers} out of {len(outcomes)} similar clients successfully repaid")
        else:
            st.warning(f"⚠️ **May Need Improvement** - Only {good_payers} out of {len(outcomes)} similar clients repaid")
        
        # Show similar cases
        st.markdown("### 👥 Your Financial Twins")
        
        similar_data = []
        for s in similar[:5]:
            similar_data.append({
                'Client ID': s.payload['client_id'],
                'Similarity': f"{s.score:.2%}",
                'Income': f"${s.payload['income']:.0f}",
                'Debt': f"${s.payload['debt']:.0f}",
                'Outcome': '✅ Repaid' if s.payload['outcome'] == 1 else '❌ Defaulted'
            })
        
        st.dataframe(pd.DataFrame(similar_data), use_container_width=True)
        st.markdown("---")
        st.subheader("🌟 Your Success Twin")
        st.markdown("**Learn from someone who started like you and succeeded**")
        
        from utils import find_success_twin, calculate_improvement_path
        
        success_twin = find_success_twin(memory, new_client, min_similarity=0.6)
        
        if success_twin:
            st.success(f"✨ We found a client {success_twin.score:.0%} similar to you who successfully repaid their loan!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Your Profile:**")
                st.write(f"💰 Income: ${income:.0f}")
                st.write(f"💳 Debt: ${debt:.0f}")
                st.write(f"📅 Seniority: {seniority} months")
                st.write(f"✅ Consistency: {payment_consistency:.0%}")
            
            with col2:
                st.markdown(f"**Success Twin ({success_twin.payload['client_id']}):**")
                st.write(f"💰 Income: ${success_twin.payload['income']:.0f}")
                st.write(f"💳 Debt: ${success_twin.payload['debt']:.0f}")
                st.write(f"📅 Seniority: {success_twin.payload['seniority_months']} months")
                st.write(f"✅ Consistency: {success_twin.payload['payment_consistency']:.0%}")
            
            # Show improvement path
            improvements = calculate_improvement_path(new_client, success_twin.payload)
            
            if improvements:
                st.markdown("### 🎯 Your Path to Approval")
                st.markdown("**Based on your Success Twin's profile, here's what you can improve:**")
                
                for imp in improvements:
                    with st.expander(f"📊 {imp['factor']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Your Current:**")
                            st.write(imp['current'])
                        with col2:
                            st.write(f"**Target:**")
                            st.write(imp['target'])
                        with col3:
                            st.write(f"**Action:**")
                            st.write(imp['action'])
            else:
                st.info("🎉 You're already very close to your Success Twin's profile!")
        else:
            st.warning("No close success twin found. Try improving your financial metrics.")

#############################################
# ADMIN COMMAND CENTER
#############################################
elif dashboard == "⚙️ Admin Command Center":
    st.header("Admin Command Center")
    
    st.markdown("### Vector Space Explorer")
    
    # Load all data for visualization
    df = pd.read_csv('synthetic_clients.csv')
    
    # Simple 2D projection using first 2 features (income, debt)
    df['income_norm'] = df['income'] / 5000
    df['debt_norm'] = df['debt'] / 10000
    
    fig = go.Figure()
    
    # Plot good payers
    good = df[df['outcome'] == 1]
    fig.add_trace(go.Scatter(
        x=good['income_norm'],
        y=good['debt_norm'],
        mode='markers',
        name='Good Payers',
        marker=dict(color='#51cf66', size=8, opacity=0.6),
        text=good['client_id'],
        hovertemplate='<b>%{text}</b><br>Income: %{x:.2f}<br>Debt: %{y:.2f}'
    ))
    
    # Plot defaulters
    bad = df[df['outcome'] == 0]
    fig.add_trace(go.Scatter(
        x=bad['income_norm'],
        y=bad['debt_norm'],
        mode='markers',
        name='Defaulters',
        marker=dict(color='#ff6b6b', size=8, opacity=0.6),
        text=bad['client_id'],
        hovertemplate='<b>%{text}</b><br>Income: %{x:.2f}<br>Debt: %{y:.2f}'
    ))
    
    fig.update_layout(
        title="Client Vector Space (Income vs Debt)",
        xaxis_title="Normalized Income",
        yaxis_title="Normalized Debt",
        height=600,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Stats
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
