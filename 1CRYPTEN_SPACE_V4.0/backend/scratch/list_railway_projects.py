
import requests
import json

def list_projects(token):
    url = "https://backboard.railway.com/graphql/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query = """
    query {
      projects {
        edges {
          node {
            id
            name
          }
        }
      }
    }
    """
    
    try:
        response = requests.post(url, headers=headers, json={"query": query})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    token = "5dee6975-be12-4a3a-ac53-6dc851c0bf13"
    result = list_projects(token)
    print(json.dumps(result, indent=2))
