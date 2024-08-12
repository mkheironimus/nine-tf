"""
Changed attributes
"""

import hashlib
import json

from .utility import dd_name

class AttributeChanges:
    """Format attribute changes"""
    masked_note = 'sensitive'
    unknown_note = '(known after apply)'

    def __init__(self, masked=None, unknown=None, change_id=None, diff=None):
        """Attribute changes for one resource

        Keyword arguments:
        masked -- sensitve attribute names
        unknown -- unknown-after-apply attribute names
        change_id -- change ID, if any
        diff -- diff to immediately process
        """
        self.masked = tuple(masked or [])
        self.unknown = tuple(unknown or [])
        self.change_id = change_id
        self.change = []
        if diff is not None:
            self.process(diff=diff)

    def __str__(self):
        """For printing"""
        return str(self.change)

    def hash_value(self, value, should):
        """Helper to hash a value only if necessary

        Keyword arguments:
        value -- attribute value
        should -- should it be hashed with a note
        """
        if value and should:
            sha = hashlib.sha256(json.dumps(value).encode('utf-8')).hexdigest()
            return f'{self.masked_note}:{sha}'
        return value

    def format(self, name, old=None, new=None):
        """Build attribute change entry

        Keyword arguments:
        name -- attribute name
        old -- previous value (if any)
        new -- planned value (if any)
        """
        attr = dd_name(name)
        should_hash = attr.startswith(self.masked)
        record = {
            'attribute': attr,
            'old': self.hash_value(value=old, should=should_hash),
            'new': self.hash_value(value=new, should=should_hash)
        }
        if new is None and attr.startswith(self.unknown):
            record['new'] = self.unknown_note
        if self.change_id:
            record['change_id'] = self.change_id
        return record

    def process(self, diff):
        """Process DeepDiff results

        Keyword arguments:
        diff -- DeepDiff object
        """
        self.change = []
        for change, data in diff.to_dict().items():
            if change.endswith('_changed'):
                for name, update in data.items():
                    self.change.append(self.format(name=name,
                             old=update['old_value'], new=update['new_value']))
            elif change.endswith('_added'):
                for name, update in data.items():
                    self.change.append(self.format(name=name, new=update))
            elif change.endswith('_removed'):
                for name, update in data.items():
                    self.change.append(self.format(name=name, old=update))

    def attributes(self, diff=None):
        """Return data as a list of dicts

        Keyword arguments:
        diff -- DeepDiff object
        """
        if diff is not None:
            self.process(diff)
        return self.change

    def as_dict(self, diff=None):
        """Return data as a dict instead of a list of dicts

        Keyword arguments:
        diff -- DeepDiff object
        """
        return {a['attribute']: {'old': a['old'], 'new': a['new']}
                for a in self.attributes(diff=diff)}

    def as_tuple(self, diff=None):
        """Return data as a list of tuples instead of a list of dicts

        Keyword arguments:
        diff -- DeepDiff object
        """
        results = []
        for attr in self.attributes(diff=diff):
            entry = [attr['attribute'], attr['old'], attr['new']]
            cid = attr.get('change_id')
            if cid:
                entry.append(cid)
            results.append(tuple(entry))
        return results

class AttributeChangesTuple(AttributeChanges):
    """Natively store as tuples"""

    def format(self, name, old=None, new=None):
        """Build attribute change entry

        Keyword arguments:
        name -- attribute name
        old -- previous value (if any)
        new -- planned value (if any)
        """
        attr = dd_name(name)
        should_hash = attr.startswith(self.masked)
        record = [
            attr,
            self.hash_value(value=old, should=should_hash),
            self.hash_value(value=new, should=should_hash)
        ]
        if new is None and attr.startswith(self.unknown):
            record[2] = self.unknown_note
        if self.change_id:
            record.append(self.change_id)
        return tuple(record)
