"""Deterministic demonstration adapter; no model or enterprise service is called."""
from typing import Protocol


class AgentAdapter(Protocol):
    def generate(self, spec: dict, feedback: list[dict]) -> str: ...
    def reflect(self, gates: list[dict]) -> dict: ...


class DemoAgent:
    def generate(self, spec, feedback):
        # Intentionally incomplete first draft so the demo exercises repair.
        if not feedback:
            return '''def can_book(capacity, booked, requested):
    return requested >= 0 and booked + requested <= capacity
'''
        return '''def can_book(capacity, booked, requested):
    return (capacity >= 0 and booked >= 0 and requested > 0
            and booked + requested <= capacity)
'''

    def reflect(self, gates):
        failed = [case['id'] for gate in gates for case in gate.get('cases', []) if not case['passed']]
        return {
            'failed_criteria': failed,
            'diagnosis': 'The draft checked available seats but omitted input-boundary rules.',
            'next_action': 'Require a positive request and nonnegative capacity and booked count; rerun all checks.',
            'source': 'scripted demo adapter',
        }
