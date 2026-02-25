from rca_generator import generate_rca

query = "P2 - Travel page returning 404 error after deployment"

result = generate_rca(query)

print("\n===== RCA RESULT =====\n")
print(result)