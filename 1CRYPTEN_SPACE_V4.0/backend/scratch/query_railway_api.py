
import requests
import json

def query_railway(token, project_id):
    url = "https://backboard.railway.com/graphql/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Query simplificada para v2
    query = """
    query GetProject($id: String!) {
      project(id: $id) {
        name
        services {
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
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "text": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    token = "5dee6975-be12-4a3a-ac53-6dc851c0bf13"
    project_id = "9ba72cc0-165c-453d-a176-2b9711eb33eb"
    
    result = query_railway(token, project_id)
    print(json.dumps(result, indent=2))
