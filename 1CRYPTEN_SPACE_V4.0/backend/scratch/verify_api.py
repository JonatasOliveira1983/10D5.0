import asyncio
import httpx
import json

async def check_slots():
    async with httpx.AsyncClient() as client:
        try:
            # Use localhost to hit the local server
            response = await client.get("http://127.0.0.1:8085/api/slots")
            if response.status_code == 200:
                slots = response.json()
                print(f"Status Code: {response.status_code}")
                # Print the structure of the first active slot found
                for slot in slots:
                    if slot.get('symbol'):
                        print(f"Slot {slot.get('id')} ({slot.get('symbol')}):")
                        print(json.dumps(slot, indent=2))
                        return
                print("No active slots found in API response.")
            else:
                print(f"Error: Status code {response.status_code}")
        except Exception as e:
            print(f"Failed to connect to API: {e}")

if __name__ == "__main__":
    asyncio.run(check_slots())
