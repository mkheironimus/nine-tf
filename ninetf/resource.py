"""
Changed resources
"""

import json
import uuid

import deepdiff

from .utility import dd_name
from .attribute import AttributeChanges, AttributeChangesTuple

def find_true(data):
    """Get True elements from sensitive/unknown structures

    Keyword arguments:
    data -- data structure to check
    """
    search = deepdiff.DeepSearch(data, True) if data else {}
    return {dd_name(a) for a in search.get('matched_values', [])}


class ResourceChange:
    """Resource change"""
    attribute_formatter = AttributeChanges

    def __init__(self, record, change_id=None, full=False, as_tuple=False):
        """A resource change record

        Keyword arguments:
        record -- single change record from plan, with "change" subkey
        change_id -- use a change ID, or True to generate UUID
        full -- include full before/after fields in change record
        as_tuple -- format record as tuples
        """
        self.as_tuple = as_tuple
        self.change_id = change_id
        if change_id is True:
            self.change_id = str(uuid.uuid4())
        action = '-'.join(record['change']['actions'])
        reason = record.get('action_reason')
        if action in ('create-delete', 'delete-create'):
            reason = f'{action} {reason or ""}'.strip()
            action = 'replace'
        if record['change'].get('replace_paths'):
            reason = f'{reason} {json.dumps(record["change"]["replace_paths"])}'.strip()
        before = record['change'].get('before')
        after = record['change'].get('after')
        self.attribute_change = None
        if action in ('update', 'replace'):
            mask_before = find_true(record['change'].get('before_sensitive'))
            mask_after = find_true(record['change'].get('after_sensitive'))
            self.attribute_change = self.attribute_formatter(
                unknown=find_true(record['change'].get('after_unknown')),
                masked=mask_before.union(mask_after),
                change_id=self.change_id,
                diff=deepdiff.DeepDiff(before, after, verbose_level=2)
            )
        self.resource_change = {
            'address': record['address'],
            'action': action,
            'rename_from': record.get('previous_address'),
            'reason': reason,
            'deposed': record.get('deposed', False),
        }
        if full:
            self.resource_change['before'] = before
            self.resource_change['after'] = after

    def __str__(self):
        """For printing"""
        return str({
            'resource': self.resource(),
            'attributes': self.attributes()
        })

    def attributes(self):
        """Return changed attributes"""
        if not self.attribute_change:
            return self.attribute_change
        if self.as_tuple:
            return self.attribute_change.as_tuple()
        return self.attribute_change.attributes()

    def resource(self):
        """Return resource change spec"""
        data = self.resource_change
        if self.as_tuple:
            entry = [
                data['address'],
                data['action'],
                data['rename_from'],
                data['reason'],
                data['deposed'],
            ]
            before = data.get('before')
            if before is not None:
                entry.extend([before, data['after']])
            if self.change_id:
                entry.append(self.change_id)
            data = tuple(entry)
        elif self.change_id:
            data = { **self.resource_change, 'change_id': self.change_id }
        return data

    def record(self):
        """Consolidated single record"""
        return (self.resource(), self.attributes())

class ResourceChangeTuple(ResourceChange):
    """Resource change"""
    attribute_formatter = AttributeChangesTuple

    def resource(self):
        """Return resource change spec"""
        entry = [
            self.resource_change['address'],
            self.resource_change['action'],
            self.resource_change['rename_from'],
            self.resource_change['reason'],
            self.resource_change['deposed'],
        ]
        before = self.resource_change.get('before')
        if before is not None:
            entry.extend([before, self.resource_change['after']])
        if self.change_id:
            entry.append(self.change_id)
        return tuple(entry)
