import os
import json
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

# Step 1: Core Agent Class
class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.system = f"You are the {name}. {role}"

    def run(self, task: str, context: str = "") -> str:
        prompt = f"Context from previous steps:\n{context}\n\nYour specific task: {task}" if context else task
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()


    # Step 2: Define Specialist Agents & Worker Registry

    # 1. Specialized Workers
researcher = Agent(
    name="Researcher",
    role="Extract the 3 core principles and 1 common pitfall of the topic. Output concise bullet points only."
)

analogy_crafter = Agent(
    name="AnalogyCrafter",
    role="Take technical concepts and explain them using a relatable, non-technical everyday analogy (e.g., cooking, post offices, traffic)."
)

code_builder = Agent(
    name="CodeBuilder",
    role="Provide a minimal, working, 10-to-15-line Python script demonstrating the topic with inline comments."
)

reviewer = Agent(
    name="Reviewer",
    role="Critique the tutorial draft for beginners. If it is accurate, engaging, and under 300 words, start your response with 'APPROVED'. Otherwise, list the exact bullet points to fix."
)

# 2. Worker allow-list registry
WORKERS = {
    "researcher": researcher,
    "analogy_crafter": analogy_crafter,
    "code_builder": code_builder,
}

# Step 3: Planner / Orchestrator
PLANNER_SYSTEM = """You are the master coordinator for a technical education team.
Given a topic, create a step-by-step workflow assigning tasks to these workers:
- researcher
- analogy_crafter
- code_builder

Reply ONLY with valid JSON in this format:
{
  "steps": [
    {"worker": "worker_name", "task": "concise task description"}
  ]
}"""

def plan_workflow(goal: str) -> list:
    print(f"\n[Orchestrator] Planning steps for: '{goal}'...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": goal},
        ],
        response_format={"type": "json_object"},
    )
    plan_data = json.loads(response.choices[0].message.content)
    return plan_data.get("steps", [])

# Step 4: Execution Loop with Evaluator-Optimizer Pattern
def orchestrate_lesson(topic: str, max_revisions: int = 2) -> str:
    # Step A: Generate dynamic plan
    steps = plan_workflow(topic)
    shared_context = ""
    
    # Step B: Worker hand-offs
    for step in steps:
        worker_key = step["worker"].lower()
        task = step["task"]
        
        # Fallback safeguard in case planner invents a worker
        worker = WORKERS.get(worker_key, code_builder)
        
        print(f" -> Handing off to [{worker.name}] for: {task}")
        result = worker.run(task=task, context=shared_context)
        
        # Append to shared memory
        shared_context += f"\n--- [{worker.name} Output] ---\n{result}\n"

    # Step C: Combine into an initial draft
    draft = shared_context
    print("\n[Orchestrator] Assembling draft and initiating review...")

    # Step D: Critic / Evaluator loop
    for revision in range(max_revisions):
        print(f" -> Review cycle {revision + 1}...")
        review = reviewer.run(
            task="Review this lesson draft. Reply 'APPROVED' or list required fixes.",
            context=draft
        )

        if review.strip().upper().startswith("APPROVED"):
            print(" -> Draft APPROVED by Reviewer!")
            break
        
        print(" -> Reviewer requested adjustments. Polishing...")
        # Route revisions back to the AnalogyCrafter or CodeBuilder based on need
        draft = analogy_crafter.run(
            task=f"Refine the draft to address these reviewer comments:\n{review}",
            context=draft
        )

    return draft  

if __name__ == "__main__":
    goal = "Create a beginner-friendly lesson on Python Generators and the yield keyword"
    final_output = orchestrate_lesson(goal)
    
    print("\n" + "=" * 50)
    print("FINAL DELIVERABLE:")
    print("=" * 50)
    print(final_output)