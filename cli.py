import asyncio
import httpx


async def main():
    base_url = "http://localhost:8000"

    while True:
        print("\nSelect an action:")
        print("1. Crawl a URL")
        print("2. Generate content")
        print("3. Add a chat turn")
        print("4. Get chat history")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            url = input("Enter the URL to crawl: ")
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{base_url}/crawl", json={"url": url})
                print(response.json())
        elif choice == "2":
            prompt = input("Enter the prompt: ")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/generate", json={"prompt": prompt}
                )
                print(response.json())
        elif choice == "3":
            user_id = input("Enter the user ID: ")
            message = input("Enter the message: ")
            role = input("Enter the role: ")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/history/add",
                    json={"user_id": user_id, "message": message, "role": role},
                )
                print(response.json())
        elif choice == "4":
            user_id = input("Enter the user ID: ")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/history/get/{user_id}")
                print(response.json())
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())