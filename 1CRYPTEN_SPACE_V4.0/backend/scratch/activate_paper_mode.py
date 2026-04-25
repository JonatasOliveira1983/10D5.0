
import requests
import json

token = "c2b33c6a-5b96-4ec4-93a5-f79e0319eb6e"
service_id = "ce913a1d-f8e3-428e-b657-1f38506d29ce"
project_id = "9ba72cc0-165c-453d-a176-2b9711eb33eb"
env_id = "8eb265ac-5e41-4a1e-81ca-2cce1a3d205f"

vars_to_set = {
    "BYBIT_EXECUTION_MODE": "PAPER",
    "BYBIT_SIMULATED_BALANCE": "100.0"
}

query = """
mutation variableUpsert($input: VariableUpsertInput!) {
  variableUpsert(input: $input)
}
"""

for name, value in vars_to_set.items():
    variables = {
        "input": {
            "projectId": project_id,
            "environmentId": env_id,
            "serviceId": service_id,
            "name": name,
            "value": value
        }
    }
    response = requests.post(
        "https://backboard.railway.app/graphql/v2",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": query, "variables": variables}
    )
    print(f"Set {name}={value}: {response.json()}")
