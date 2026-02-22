#!/usr/bin/env python3
"""Check CrewAI instance methods"""
from crewai import Crew, Agent, Task, LLM
import os

os.environ["OPENAI_API_KEY"] = "NA"

# Create a dummy LLM
llm = LLM(model="ollama/llama3:8b", base_url="http://127.0.0.1:11434")

# Create a dummy agent
agent = Agent(
    role="Test",
    goal="Test agent",
    backstory="Test",
    llm=llm
)

# Create a dummy task
task = Task(
    description="Test task",
    agent=agent,
    expected_output="Test output"
)

# Create crew instance
try:
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process="sequential",
        verbose=True
    )
    
    print("="*60)
    print("CREW INSTANCE METHODS")
    print("="*60)
    
    all_methods = [m for m in dir(crew) if not m.startswith('_')]
    print(f"\nPublic methods ({len(all_methods)}):")
    for m in sorted(all_methods):
        print(f"  - {m}")
    
    print("\n" + "="*60)
    print("CHECKING KEY METHODS")
    print("="*60)
    
    for method in ['kickoff', 'run', 'execute', 'start']:
        has_it = hasattr(crew, method)
        callable_it = callable(getattr(crew, method, None)) if has_it else False
        print(f"  crew.{method:<10} - exists: {has_it}, callable: {callable_it}")
        
except Exception as e:
    print(f"Error creating crew: {e}")
    import traceback
    traceback.print_exc()
