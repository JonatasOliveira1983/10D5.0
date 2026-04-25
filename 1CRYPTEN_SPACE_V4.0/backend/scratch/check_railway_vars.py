
import requests
import json

def get_service_variables(token, service_id, project_id, environment_id):
    url = "https://backboard.railway.com/graphql/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query = """
    query GetVariables($serviceId: String!, $projectId: String!, $environmentId: String!) {
      variables(serviceId: $serviceId, projectId: $projectId, environmentId: $environmentId)
    }
    """
    
    variables = {
        "serviceId": service_id,
        "projectId": project_id,
        "environmentId": environment_id
    }
    
    try:
        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_environments(token, project_id):
    url = "https://backboard.railway.com/graphql/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    query = """
    query GetProject($id: String!) {
      project(id: $id) {
        environments {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
    """
    variables = {"id": project_id}
    try:
        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    token = "c2b33c6a-5b96-4ec4-93a5-f79e0319eb6e"
    project_id = "9ba72cc0-165c-453d-a176-2b9711eb33eb"
    service_id = "ce913a1d-f8e3-428e-b657-1f38506d29ce" # 10D5.0
    
    # 1. Get Environment ID
    envs = get_environments(token, project_id)
    env_id = envs['data']['project']['environments']['edges'][0]['node']['id']
    print(f"Environment ID: {env_id}")
    
    # 2. Get Variables
    vars_res = get_service_variables(token, service_id, project_id, env_id)
    print(json.dumps(vars_res, indent=2))
