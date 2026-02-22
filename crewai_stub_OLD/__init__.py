"""Minimal CrewAI package stub for tests."""

class Crew:
    def __init__(self, *args, **kwargs):
        pass

class Process:
    def __init__(self, *args, **kwargs):
        pass

class Agent:
    def __init__(self, *args, **kwargs):
        self.role = kwargs.get('role', '')

class LLM:
    def __init__(self, *args, **kwargs):
        self.model = kwargs.get('model', '')

class Task:
    def __init__(self, *args, **kwargs):
        pass
