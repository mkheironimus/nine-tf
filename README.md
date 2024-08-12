# 9.tf (nine-tf)

*What plan will you follow now?*

Attempt to use Python to process JSON-format Terraform/OpenTofu plans to summarize resource changes.

## Plans

Generate the plan:
```bash
terraform plan -out plan.out
terraform show -json plan.out > plan.json
```

Load it:
```python
from ninetf import PlanChanges
print(PlanChanges(file='plan.json').records())
```

## State

Generate the cooked state:
```bash
terraform show -json > state.json
```

Load it:
```python
from ninetf import State
print(State(file='state.json').resources())
```

