from fastmcp import Client
import asyncio


async def main():
    # The client will automatically handle Google OAuth
    async with Client("http://localhost:8000/mcp", auth="oauth") as client:
        # First-time connection will open Google login in your browser
        print("✓ Authenticated with Google!")

        # Test the protected tool
        result = await client.call_tool("list_datasets")
        print(result)

        result = await client.call_tool("list_tables", arguments={"dataset_id": "powerbi"})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
