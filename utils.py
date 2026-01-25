# Helper functions 
def find_success_twin(memory, client_data, min_similarity=0.7):
    """
    Find a successful client who started with similar profile
    """
    # Search for similar clients who succeeded (outcome=1)
    all_similar = memory.find_similar_clients(client_data, top_k=50)
    
    # Filter for good payers only
    good_payers = [s for s in all_similar if s.payload['outcome'] == 1 and s.score >= min_similarity]
    
    if good_payers:
        # Return the most similar successful case
        return good_payers[0]
    
    return None

def calculate_improvement_path(current_client, success_twin_payload):
    """
    Calculate what needs to change to match success twin
    """
    improvements = []
    
    # Income gap
    income_gap = success_twin_payload['income'] - current_client['income']
    if abs(income_gap) > 100:
        improvements.append({
            'factor': 'Income',
            'current':f"${current_client['income']:.0f}",
            "target": f"${success_twin_payload['income']:.0f}",
        'action': f"{'Increase' if income_gap > 0 else 'Decrease'} by ${abs(income_gap):.0f}"
    })
    #Debt gap
    debt_gap = current_client['debt'] - success_twin_payload['debt']
    if abs(debt_gap) > 200:
        improvements.append({
            'factor': 'Debt',
            'current': f"${current_client['debt']:.0f}",
            'target': f"${success_twin_payload['debt']:.0f}",
            'action': f"{'Reduce' if debt_gap > 0 else 'Increase'} by ${abs(debt_gap):.0f}"
        })

    # Seniority gap
    seniority_gap = success_twin_payload['seniority_months'] - current_client['seniority_months']
    if abs(seniority_gap) > 3:
        improvements.append({
            'factor': 'Business Seniority',
            'current': f"{current_client['seniority_months']} months",
            'target': f"{success_twin_payload['seniority_months']} months",
            'action': f"Build {abs(seniority_gap)} more months of track record"
        })

    # Payment consistency
    consistency_gap = success_twin_payload['payment_consistency'] - current_client['payment_consistency']
    if abs(consistency_gap) > 0.1:
        improvements.append({
            'factor': 'Payment Consistency',
            'current': f"{current_client['payment_consistency']:.0%}",
            'target': f"{success_twin_payload['payment_consistency']:.0%}",
            'action': f"Improve consistency by {abs(consistency_gap):.0%}"
        })

    return improvements
        
