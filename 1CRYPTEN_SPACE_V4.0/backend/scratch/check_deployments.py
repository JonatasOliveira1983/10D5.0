
import requests
import json

def get_latest_deployments(token, service_id):
    url = "https://backboard.railway.com/graphql/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query = """
    query GetDeployments($serviceId: String!) {
      service(id: $serviceId) {
        name
        deployments {
          edges {
            node {
              id
              status
              createdAt
            }
          }
        }
      }
    }
    """
    
    variables = {"serviceId": service_id}
    
    try:
        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    token = "c2b33c6a-5b96-4ec4-93a5-f79e0319eb6e"
    service_id = "ce913a1d-f8e3-428e-b657-1f38506d29ce" # 10D5.0
    
    result = get_latest_deployments(token, service_id)
    print(json.dumps(result, indent=2))
