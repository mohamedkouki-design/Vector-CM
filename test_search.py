from qdrant_manager import CreditMemory as QdrantManager
from embeddings import create_embedding

# Initialize
qm = QdrantManager(host="localhost", port=6333)

# Test client
test_client = {
    'archetype': 'market_vendor',
    'debt_ratio': 0.45,
    'years_active': 15,
    'income_stability': 0.85,
    'payment_regularity': 0.88,
    'monthly_income': 2500
}

print("🔍 Searching for similar clients...")
print(f"Query: {test_client['archetype']}, debt={test_client['debt_ratio']}")

# Create embedding
vector = create_embedding(test_client)

# Search
results = qm.client.query_points(
    collection_name="credit_history_memory",
    query=vector.tolist(),
    limit=10
)

print(f"\n✅ Found {len(results.points)} similar clients:\n")

for i, result in enumerate(results.points, 1):
    print(f"{i}. Similarity: {result.score:.3f}")
    print(f"   Client: {result.payload.get('client_id')}")
    print(f"   Outcome: {result.payload.get('outcome')}")
    print(f"   Loan Source: {result.payload.get('loan_source')}")
    print(f"   Debt Ratio: {result.payload.get('debt_ratio')}")
    print()

# Calculate repayment rate - FIXED
repaid = sum(1 for r in results.points if r.payload.get('outcome') == 'repaid')
print(f"📊 Repayment Rate: {repaid}/{len(results.points)} ({repaid/len(results.points)*100:.0f}%)")