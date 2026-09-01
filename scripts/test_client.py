from fastmcp import Client
import asyncio


async def main():
    # The client will automatically handle Google OAuth
    async with Client(
        "https://rag.projectsuite.io/mcp?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJQcm9qZWN0TUNQIiwiaXNzIjoiaHR0cHM6Ly9hcGkucHJvamVjdHN1aXRlLmlvIiwiaWF0IjoxNzU5NDA2MDQ3LCJleHAiOjE4MjI0NzgwNDcsImF1ZCI6IlByb2plY3RNQ1AiLCJzY29wZSI6InJlYWQgd3JpdGUgYWRtaW4ifQ.HDzHFBHPJ4g4qVop2fldNxscDvR4gLhTk4gt8yiSV4A_zYL5VEkTOgB0VUbvJhrXRdICXx-x3xQLP7AGW3eMZ_YnMItZbYiFgLt1aWwBqDyICv4jmeauO4SjGzsE34GAZDlH8DviJFHJG5uCO9g1ayurvLpScMolKT0lzJNczI00-vM5tpFuk6RbFgNCpZiDg8fE_F8IT6Mf7ke75rw7XVNO9kOAzmDPTamCAzVRi02fVO_4Bg3tj9qrUEKhoVoF_ZIbp2PwMIMCULw5E7XR9mr0HIST3NnTTPzFWxJYjFoYr7-cPbBnoKiOUL1POH66OZ02KYevydN-_kCw8o3kCA",
        auth="oauth",
    ) as client:
        # First-time connection will open Google login in your browser
        print("✓ Authenticated with Google!")

        # Test the protected tool
        result = await client.call_tool("list_datasets")
        print(result)

        result = await client.call_tool("list_tables", arguments={"dataset_id": "powerbi"})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
