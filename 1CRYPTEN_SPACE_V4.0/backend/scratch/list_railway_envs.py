
import requests
import json

token = "c2b33c6a-5b96-4ec4-93a5-f79e0319eb6e"
project_id = "9ba72cc0-165c-453d-a176-2b9711eb33eb"

query = """
query project($id: String!) {
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

response = requests.post(
    "https://backboard.railway.app/graphql/v2",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": query, "variables": variables}
)

print(json.dumps(response.json(), indent=2))
