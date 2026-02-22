#!/usr/bin/env python3
"""
Quick script to check CrewAI API methods
"""
from crewai import Crew, Agent, Task, LLM
import inspect

# Check Crew class methods
print("="*60)
print("CREWAI CREW CLASS METHODS")
print("="*60)

all_attrs = dir(Crew)
public_methods = [m for m in all_attrs if not m.startswith('_')]

print(f"\nPublic attributes/methods ({len(public_methods)}):")
for method in sorted(public_methods):
    print(f"  - {method}")

# Check if specific methods exist
print("\n" + "="*60)
print("CHECKING SPECIFIC METHODS")
print("="*60)

methods_to_check = ['kickoff', 'run', 'execute', 'start', 'invoke', 'process']
for method in methods_to_check:
    exists = hasattr(Crew, method)
    print(f"  Crew.{method:<12} exists: {exists}")

# Try to see method signatures
print("\n" + "="*60)
print("METHOD SIGNATURES")
print("="*60)

for attr in ['kickoff', 'run', 'execute']:
    if hasattr(Crew, attr):
        try:
            sig = inspect.signature(getattr(Crew, attr))
            print(f"\n  Crew.{attr}{sig}")
        except:
            print(f"\n  Crew.{attr} - Could not get signature")

print("\n" + "="*60)
print("CREWAI VERSION")
print("="*60)
try:
    import crewai
    if hasattr(crewai, '__version__'):
        print(f"  Version: {crewai.__version__}")
    else:
        print(f"  Version: Unknown (no __version__ attribute)")
except:
    print("  Could not determine version")

print()
