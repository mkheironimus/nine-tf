"""
Process state JSON (TF* show -json)
"""

import json
import uuid

class State:
    """Process current state"""

    def __init__(self, file=None, stream=None, state_id=None, as_tuple=False):
        """Current state representation

        Keyword arguments:
        file -- JSON file to load
        stream -- open file stream
        state_id -- use a state ID, or True to generate UUID
        as_tuple -- format as list of tuples instead of dicts
        """
        self.as_tuple = as_tuple
        self.state_id = state_id
        if state_id is True:
            self.state_id = str(uuid.uuid4())
        self.state_resources = []
        if stream:
            self.stream(stream)
        elif file:
            self.file(file)

    def resources(self, as_tuple=None):
        """Return summarized resources from state"""
        if as_tuple is None:
            as_tuple = self.as_tuple
        if not as_tuple:
            return self.state_resources
        resources = []
        for res in self.state_resources:
            record = [
                res['address'],
                res['mode'],
                res['provider'],
                res['type'],
                res['name'],
                res['index'],
            ]
            state_id = res.get('state_id')
            if state_id:
                record.append(state_id)
            resources.append(tuple(record))
        return resources

    def format_resource(self, resource):
        """Format a single resource record

        Keyword arguments:
        resource -- resource structure
        """
        record = {
            'address': resource['address'],
            'mode': resource['mode'],
            'provider': resource['provider_name'],
            'type': resource['type'],
            'name': resource['name'],
            'index': str(resource.get('index', '')) or None,
        }
        if self.state_id:
            record['state_id'] = self.state_id
        return record

    def load_module(self, module):
        """Recursively load state structure

        Keyword arguments:
        module -- module to read
        """
        for res in module.get('resources', []):
            self.state_resources.append(self.format_resource(resource=res))
        for sub in module.get('child_modules', []):
            self.state_resources.extend(self.load_module(module=sub))

    def stream(self, stream):
        """Process open JSON state stream

        Keyword arguments:
        stream -- open file stream
        """
        state = json.load(stream)
        self.load_module(module=state['values']['root_module'])

    def file(self, file):
        """Load JSON state file

        Keyword arguments:
        file -- JSON file to load
        """
        with open(file, 'r', encoding='utf8') as raw:
            self.stream(stream=raw)

class StateTuple(State):
    """Natively store as list of tuples"""

    def format_resource(self, resource):
        """Format a single resource record

        Keyword arguments:
        resource -- resource structure
        """
        record = [
            resource['address'],
            resource['mode'],
            resource['provider_name'],
            resource['type'],
            resource['name'],
            str(resource.get('index', '')) or None,
        ]
        if self.state_id:
            record.append(self.state_id)
        return tuple(record)
