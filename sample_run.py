#! /usr/bin/python3

import json

from ninetf import PlanChanges, PlanChangesTuple
from ninetf import State, StateTuple

plan = 'test/plan.json'
state = 'test/state.json'

print(json.dumps({
    'PlanChanges': PlanChanges(file=plan, change_ids=True).records(),
    'PlanChangesTuple': PlanChangesTuple(file=plan, change_ids=True).records(),
    'State': State(file=state, state_id=True).resources(),
    'StateTuple': StateTuple(file=state, state_id=True).resources()
}))
