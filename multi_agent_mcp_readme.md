# 🤖 Byte-Sized Tech Educator: Multi-Agent System via MCP

An end-to-end **Multi-Agent Orchestration System** built from scratch using **Python**, **Groq LLM API**, and Anthropic's official **Model Context Protocol (MCP)** (`FastMCP`). 

No heavy black-box frameworks (like LangChain or CrewAI) are used—just clean Python control flow, specialized agent prompts, and standard Stdio MCP tool calling.

---

## 🏗️ System Architecture

This project follows the **Orchestrator-Workers** and **Evaluator-Optimizer** multi-agent patterns exposed over the **Model Context Protocol (MCP)**:

```text
+-------------------------------------------------------------------+
|                     MCP Host & Client (client.py)                 |
|  - Discovers available Agent Tools via MCP Handshake              |
|  - Manages shared memory & sequential context passing             |
|  - Triggers the Evaluator review loop                             |
+---------------------------------+---------------------------------+
                                  |
                         Stdio Pipe (JSON-RPC)
                                  |
+---------------------------------v---------------------------------+
|                     FastMCP Server (server.py)                    |
|                                                                   |
|  [Tool 1] research_topic       --> Extracts core facts & pitfalls |
|  [Tool 2] craft_analogy        --> Creates everyday metaphors     |
|  [Tool 3] generate_code_demo   --> Writes clean Python snippets   |
|  [Tool 4] review_draft         --> Evaluates & approves quality   |
+-------------------------------------------------------------------+
```

### 👥 Meet the Specialist Agents (MCP Tools)
1. **Researcher (`research_topic`)**: Extracts the 3 core principles and 1 common pitfall of any programming topic in concise bullet points.
2. **Analogy Crafter (`craft_analogy`)**: Translates complex technical jargon into relatable, everyday real-world analogies (e.g., cooking, post offices, traffic).
3. **Code Builder (`generate_code_demo`)**: Writes a minimal, working, self-contained 10-to-15-line Python script demonstrating the concept.
4. **Quality Reviewer (`review_draft`)**: Acts as the quality gatekeeper. Evaluates the compiled lesson for beginner-friendliness and clarity, returning `APPROVED` or actionable revision feedback.

---

## 📁 Project Structure

```text
Multi-Agent-MCP/
├── server.py         # FastMCP Server exposing the 4 specialist agents as MCP tools
├── client.py         # MCP Client & Orchestrator managing tool discovery & workflow
├── .env              # Environment variables (Groq API Key)
└── README.md         # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- A free or paid **Groq API Key** from [console.groq.com](https://console.groq.com/)

### 2. Installation
Clone or navigate to your project directory, create a virtual environment, and install the required packages:

```bash
# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install MCP SDK, OpenAI client (for Groq), and python-dotenv
pip install "mcp[cli]" openai python-dotenv
```

### 3. Environment Setup
Create a `.env` file in the root directory and add your Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

---

## 💻 How to Run & Test

You only need to run the **Client** script. It automatically spawns `server.py` as a subprocess, performs the MCP protocol handshake, discovers the tools, and executes the pipeline:

```bash
python client.py
```

### Expected Terminal Output

```text
[Host] Connecting to MCP Server via Stdio...
[Host] Successfully discovered MCP Tools (Menu): ['research_topic', 'craft_analogy', 'generate_code_demo', 'review_draft']

-> [Step 1] Calling MCP Tool: 'research_topic' for 'Python Decorators and Functional Wrappers'...
   [Done] Research facts collected.

-> [Step 2] Calling MCP Tool: 'craft_analogy'...
   [Done] Real-world analogy crafted.

-> [Step 3] Calling MCP Tool: 'generate_code_demo'...
   [Done] Code snippet generated.

-> [Step 4] Calling MCP Tool: 'review_draft'...

=======================================================
MCP REVIEW FEEDBACK:
=======================================================
APPROVED. The breakdown clearly explains higher-order functions with a clean wrapper analogy and functional code snippet.

=======================================================
FINAL MCP DELIVERABLE:
=======================================================
# Lesson: Python Decorators and Functional Wrappers
...
```

---

## 🔌 Plug & Play with Claude Desktop or Cursor

Because `server.py` adheres strictly to the standard **Model Context Protocol**, you can plug these 4 specialist agents directly into **Claude Desktop** or **Cursor IDE**.

Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tech-educator-agents": {
      "command": "python",
      "args": ["D:/path/to/your/project/server.py"],
      "env": {
        "GROQ_API_KEY": "gsk_your_actual_groq_api_key_here"
      }
    }
  }
}
```

---

## ✨ Key Takeaways & Guardrails
- **Zero Framework Bloat**: Built purely with standard Python async loops and JSON structures.
- **Explicit Context Sharing**: Each agent receives accumulated context from previous steps so nothing is lost in translation.
- **Standardized Interface**: Exposing agents as `@mcp.tool()` functions makes them reusable across any MCP-compatible host application.