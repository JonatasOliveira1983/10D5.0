
import requests
import json

token = "c2b33c6a-5b96-4ec4-93a5-f79e0319eb6e"
service_id = "ce913a1d-f8e3-428e-b657-1f38506d29ce"
env_id = "8eb265ac-5e41-4a1e-81ca-2cce1a3d205f"

query = """
mutation serviceInstanceRedeploy($serviceId: String!, $environmentId: String!) {
  serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
}
"""

variables = {"serviceId": service_id, "environmentId": env_id}

response = requests.post(
    "https://backboard.railway.app/graphql/v2",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": query, "variables": variables}
)

print(json.dumps(response.json(), indent=2))
