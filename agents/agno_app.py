"""
AGNO_APP.PY - Main Agentic Application

Complete workflow:
1. DataAgent: Normalize input → raw_text
2. PromptAgent: Build LLM prompt → prompt
3. GeminiAgent: Extract profile → profile
4. SchemaBuilderAgent: Build schema → schema
5. TemplateSelectorAgent: Select template → template

Run: python -m agents.agno_app
"""

from agno import Application

from agents.core.data_agent import DataAgent
from agents.core.prompt_agent import PromptAgent
from agents.core.gemini_agent import GeminiAgent
from agents.core.schema_builder import SchemaBuilderAgent
from agents.core.template_selector_agent import TemplateSelectorAgent


def create_app():
    """Create and configure the Agno application"""
    return Application(
        name="Showcase-Portfolio-Builder",
        agents=[
            DataAgent(),           # Step 1: Normalize input
            PromptAgent(),         # Step 2: Build prompt
            GeminiAgent(),         # Step 3: Extract profile via LLM
            SchemaBuilderAgent(),  # Step 4: Build portfolio schema
            TemplateSelectorAgent(), # Step 5: Select template
        ],
    )


app = create_app()



if __name__ == "__main__":
    
    sample_input = {
        "name": "Arjun Sharma",
        "email": "arjun@example.com",
        "role": "Full Stack Developer",
        "skills": "Python, React, Docker, AWS, PostgreSQL",
        "experience": "5 years building web applications",
        "projects": "E-commerce platform, Real-time chat app, ML pipeline"
    }

    # Run workflow
    print(" Starting Showcase Portfolio Builder...")
    print(f" Input: {sample_input['name']}\n")
    
    result = app.run(input=sample_input)
    
    print("\nWorkflow Complete!")
    print(f"Schema: {result.state.get('schema', {}).get('profile_summary')}")
    print(f"Template: {result.state.get('template', {}).get('name')}")
    print(f"\nFull result stored in: result.state")