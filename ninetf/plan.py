"""
Process plan JSON (TF* show -json plan.json)
"""

import json

from .resource import ResourceChange, ResourceChangeTuple

class PlanChanges:
    """Process planned changes"""
    resource_formatter = ResourceChange

    def __init__(self, file=None, stream=None, change_ids=False, as_tuple=False):
        """Process planned changes

        Keyword arguments:
        file -- JSON file to load
        stream -- open file stream
        change_ids -- generate resource change IDs
        as_tuple -- format as list of tuples instead of list of dicts
        """
        self.as_tuple = as_tuple
        self.change_ids = bool(change_ids)
        self.changes = []
        if stream:
            self.stream(stream)
        elif file:
            self.file(file)

    def attributes(self):
        """Return all attributes"""
        return [r.attributes() for r in self.changes]

    def resources(self):
        """Return all resources"""
        return [r.resource() for r in self.changes]

    def records(self):
        """Return consolidated records"""
        return [r.record() for r in self.changes]

    def stream(self, stream):
        """Process open JSON plan stream

        Keyword arguments:
        stream -- open file stream
        """
        plan = json.load(stream)
        for resource in plan.get('resource_changes', []):
            if resource['change']['actions'] == ['read']:
                continue # Skip read-during-apply
            if resource['change']['actions'] == ['no-op'] and \
                    not resource.get('previous_address'):
                continue # Skip unchanged entries
            self.changes.append(self.resource_formatter(record=resource,
                    change_id=self.change_ids, as_tuple=self.as_tuple))
        return self.changes

    def file(self, file):
        """Load JSON plan file

        Keyword arguments:
        file -- JSON file to load
        """
        with open(file, 'r', encoding='utf8') as raw:
            return self.stream(stream=raw)

class PlanChangesTuple(PlanChanges):
    """Process planned changes"""
    resource_formatter = ResourceChangeTuple
