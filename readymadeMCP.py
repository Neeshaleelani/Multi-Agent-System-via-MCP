import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Check GROQ_API pehle, agar na mile to GROQ_API_KEY check karega
api_key = os.getenv("GROQ_API") or os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

MODEL = "openai/gpt-oss-120b"

async def test_live_mcp_server():
    # Folder ka absolute path nikalen jisko server read/write kar sakta hai
    allowed_dir = os.path.abspath("my_workspace")

    print(f"[1] Connecting to ready-made MCP server for folder: {allowed_dir}...")

    # Step A: Pre-made server ko NPX ke zariye direct launch karein (No custom server code!)
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", allowed_dir],
        env=os.environ.copy()
    )

    # Step B: Connect via standard Stdio Protocol
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # MCP Handshake & Tools auto-discovery
            await session.initialize()
            tools_result = await session.list_tools()
            
            print("\n[2] Pre-made MCP Server se auto-discover hue tools:")
            for tool in tools_result.tools:
                print(f" -> Tool: {tool.name} | Description: {tool.description}")

            # Step C: Tool Call 1 - Folder ke andar files list karna ('list_directory')
            print(f"\n[3] Calling pre-made tool 'list_directory'...")
            dir_res = await session.call_tool("list_directory", arguments={"path": allowed_dir})
            print("Files in workspace:", dir_res.content[0].text)

            # Step D: Tool Call 2 - File read karna ('read_file')
            file_to_read = os.path.join(allowed_dir, "sample_notes.txt")
            print(f"\n[4] Calling pre-made tool 'read_file' for: sample_notes.txt...")
            file_res = await session.call_tool("read_file", arguments={"path": file_to_read})
            file_content = file_res.content[0].text
            print("File Content Read:", file_content)

            # Step E: LLM ko yeh context dena (LLM + Pre-made MCP Tool Result)
            print("\n[5] LLM processing the MCP context...")
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant."},
                    {"role": "user", "content": f"Summarize and give a practical use case for this note:\n{file_content}"}
                ]
            )
            analysis = response.choices[0].message.content.strip()

            # Step F: Tool Call 3 - Nayi file generate karke write karna ('write_file')
            output_file = os.path.join(allowed_dir, "llm_summary.txt")
            print(f"\n[6] Calling pre-made tool 'write_file' to save LLM result...")
            await session.call_tool("write_file", arguments={
                "path": output_file,
                "content": analysis
            })
            print(f"Successfully written to: {output_file}")

            print("\n" + "=" * 55)
            print("LLM SUMMARY DELIVERED VIA PRE-MADE MCP TOOL:")
            print("=" * 55)
            print(analysis)

if __name__ == "__main__":
    asyncio.run(test_live_mcp_server())