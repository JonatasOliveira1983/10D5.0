
import requests
import json

def set_variable(token, service_id, project_id, environment_id, name, value):
    url = "https://backboard.railway.com/graphql/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query = """
    mutation VariableUpsert($input: VariableUpsertInput!) {
      variableUpsert(input: $input)
    }
    """
    
    variables = {
        "input": {
            "name": name,
            "value": value,
            "serviceId": service_id,
            "projectId": project_id,
            "environmentId": environment_id
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    token = "c2b33c6a-5b96-4ec4-93a5-f79e0319eb6e"
    project_id = "9ba72cc0-165c-453d-a176-2b9711eb33eb"
    service_id = "ce913a1d-f8e3-428e-b657-1f38506d29ce"
    env_id = "8eb265ac-5e41-4a1e-81ca-2cce1a3d205f"
    
    vars_to_set = {
        "DATABASE_URL": "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@postgres.railway.internal:5432/railway",
        "BYBIT_API_KEY": "ggAuWk4lVoMaKDkxsH",
        "BYBIT_API_SECRET": "aAHZbYUmRY9ukf0eIW9yVbOA3CuO0wgRKUs7",
        "BYBIT_TESTNET": "False",
        "OPENROUTER_API_KEY": "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",
        "GEMINI_API_KEY": "AIzaSyADrhHOMqiCXQpIeb41ynJLJJUOW0QhKpY",
        "GLM_API_KEY": "da252b65378447ebb0b0535e0a5da132.0cm9Kb94NjjkSCMY",
        "PORT": "8080"
    }
    
    for name, value in vars_to_set.items():
        print(f"Setting {name}...")
        res = set_variable(token, service_id, project_id, env_id, name, value)
        print(json.dumps(res, indent=2))
