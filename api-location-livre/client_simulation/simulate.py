import asyncio, httpx

BASE = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient() as client:
        # login admin
        r = await client.post(f"{BASE}/auth/connexion",
                              data={"username":"admin@example.com","password":"admin"},
                              headers={"Content-Type":"application/x-www-form-urlencoded"})
        print("Login:", r.status_code, r.json())
        token = r.json().get("access_token")

        # create book as admin
        if token:
            r = await client.post(f"{BASE}/admin/livres",
                                  json={"title":"Nouveau","author":"Auteur","year":2024,"total_copies":3},
                                  headers={"Authorization": f"Bearer {token}"})
            print("Create livre (admin):", r.status_code, r.json())

if __name__ == "__main__":
    asyncio.run(main())
