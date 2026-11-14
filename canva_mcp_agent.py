import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 1. LLM Setup (Groq API)
api_key = os.getenv("GROQ_API") or os.getenv("GROQ_API_KEY")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

MODEL = "openai/gpt-oss-120b"

async def create_canva_poster():
    # 2. Topic decide karke LLM se creative quote aur design brief banwana
    print("[1] AI Brain: Generating a creative poster brief...")
    brief_prompt = (
        "Create a short, powerful 1-sentence motivational quote about coding and consistency. "
        "Also specify a color palette theme (e.g. minimalist dark blue and neon cyan)."
    )
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": brief_prompt}],
        temperature=0.7
    )
    creative_idea = response.choices[0].message.content.strip()
    print(f" -> Generated Idea:\n{creative_idea}\n")

    # 3. Canva MCP Server parameters define karein
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@canva/mcp-server"],
        env=os.environ.copy()
    )

    print("[2] Connecting to Canva MCP Server via Stdio...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # MCP Handshake & Tools auto-discovery
            await session.initialize()
            tools_list = await session.list_tools()
            tool_names = [t.name for t in tools_list.tools]
            print(f"[3] Connected! Discovered Canva Tools: {tool_names}\n")

            # 4. Step A: Call 'generate-design' Tool
            print("[4] Calling Canva Tool: 'generate-design'...")
            design_query = f"A modern motivational poster for software developers: {creative_idea}"
            
            gen_result = await session.call_tool(
                "generate-design",
                arguments={
                    "query": design_query,
                    "design_type": "poster"
                }
            )
            
            print(" -> Canva generated candidates successfully!")
            print(" -> Response:", gen_result.content[0].text)

            print("\n" + "=" * 50)
            print("DESIGN READY!")
            print("=" * 50)
            print("Aapka design generate ho gaya hai aur direct Canva me open hone ke liye ready hai!")

if __name__ == "__main__":
    asyncio.run(create_canva_poster())