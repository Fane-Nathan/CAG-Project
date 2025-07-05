import asyncio
import httpx
import os


async def main():
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    while True:
        print("\nSelect an action:")
        print("1. Crawl a URL")
        print("2. Generate content")
        print("3. Add a chat turn")
        print("4. Get chat history")
        print("5. Cache-Augmented Generation (CAG)")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            url = input("Enter the URL to crawl: ")
            use_cache = input("Use cache? (y/n, default: y): ").lower() != 'n'
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{base_url}/crawl", json={"url": url, "use_cache": use_cache})
                data = response.json()
                print(f"Markdown content: {data['markdown'][:200]}...")
                print(f"Cached: {data['cached']}")
                if data.get('timestamp'):
                    print(f"Timestamp: {data['timestamp']}")
        elif choice == "2":
            prompt = input("Enter the prompt: ")
            use_cache = input("Use cache? (y/n, default: y): ").lower() != 'n'
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{base_url}/generate", json={"prompt": prompt, "use_cache": use_cache}
                )
                data = response.json()
                print(f"Response: {data['text']}")
                print(f"Cached: {data['cached']}")
        elif choice == "3":
            user_id = input("Enter the user ID: ").strip()
            if not user_id:
                print("Error: User ID cannot be empty")
                continue
            message = input("Enter the message: ").strip()
            if not message:
                print("Error: Message cannot be empty")
                continue
            role = input("Enter the role (user/assistant): ").strip() or "user"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/history/add",
                    json={"user_id": user_id, "message": message, "role": role},
                )
                if response.status_code == 200:
                    print(response.json())
                else:
                    print(f"Error: {response.status_code} - {response.text}")
        elif choice == "4":
            user_id = input("Enter the user ID: ").strip()
            if not user_id:
                print("Error: User ID cannot be empty")
                continue
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/history/get/{user_id}")
                if response.status_code == 200:
                    print(response.json())
                else:
                    print(f"Error: {response.status_code} - {response.text}")
        elif choice == "5":
            print("\n=== Cache-Augmented Generation ===")
            url = input("Enter the URL to analyze: ")
            query = input("Enter your query about the content: ")
            user_id = input("Enter user ID (optional, press Enter to skip): ").strip() or None
            use_cache = input("Use cache? (y/n, default: y): ").lower() != 'n'
            include_history = input("Include chat history? (y/n, default: n): ").lower() == 'y'
            
            cag_request = {
                "url": url,
                "query": query,
                "use_cache": use_cache,
                "include_history": include_history
            }
            if user_id:
                cag_request["user_id"] = user_id
            
            print("\nProcessing... This may take a moment.")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{base_url}/cag", json=cag_request)
                data = response.json()
                
                print(f"\n=== CAG Response ===")
                print(f"Query: {data['query']}")
                print(f"URL: {data['url']}")
                print(f"Response: {data['response']}")
                print(f"\n=== Metadata ===")
                print(f"Crawl cached: {data['crawl_cached']}")
                print(f"LLM cached: {data['llm_cached']}")
                print(f"Processing time: {data['processing_time']:.2f}s")
                if data.get('sources'):
                    print(f"Page title: {data['sources'].get('title', 'N/A')}")
                    print(f"Status code: {data['sources'].get('status_code', 'N/A')}")
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())