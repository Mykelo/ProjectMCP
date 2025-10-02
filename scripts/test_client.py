from fastmcp import Client
import asyncio


async def main():
    # The client will automatically handle Google OAuth
    async with Client("https://rag.projectsuite.io/mcp?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJQcm9qZWN0TUNQIiwiaXNzIjoiaHR0cHM6Ly9hcGkucHJvamVjdHN1aXRlLmlvIiwiaWF0IjoxNzU5NDAxMDk1LCJleHAiOjE3NTk0MDQ2OTUsImF1ZCI6IlByb2plY3RNQ1AiLCJzY29wZSI6InJlYWQgd3JpdGUgYWRtaW4ifQ.ngB0CO_JmONwP3BWlRoOiBEls3mfb_qjQBYXCX0q_O3glOqmPcmWHhYlKt1s1CDu66ZAZw3SHMlnTVUPhn6L44kXMvaET55wXZAOddEp2zqKnP2GSt927LdTBmuN1EBsrAn1tMlGxaIPGW9AsVca0T4h5MeZda2PeGrTQFaUch7QMufRjmtrtUJlvaaoxGzTEPiDbQzQ9XSfNRd5az29qAfmUGwUUWzjf61IvuCGl8fA73Ss1XlIBhcXP-oTS6BDIi_DwzVqcm2ZZU09ufj7u6FJWhJFytM9uoRZrGhbYHOgIGALVFid5S-s0-Px4VdtbF6MVFUtnkB_e_tHSuwiSQ", auth="oauth") as client:
        # First-time connection will open Google login in your browser
        print("✓ Authenticated with Google!")

        # Test the protected tool
        result = await client.call_tool("list_datasets")
        print(result)

        result = await client.call_tool("list_tables", arguments={"dataset_id": "powerbi"})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
