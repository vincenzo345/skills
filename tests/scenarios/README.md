# Workbench route scenarios

These five fixtures are executable route contracts, not narratives. Each records its planning destination, evidence and context, capabilities already authorized, expected stage path, uncertainty-map dependencies, material decisions, authorization outcomes, artifacts, stopping point, terminal disposition, and route-expansion triggers.

Run them with:

```powershell
python -B scripts/validate-workbench.py
```

The validator checks schema shape plus cross-field rules such as no implementation without implementation authorization, no release without deployment authorization, known map dependencies, allowed route destinations, and separation of decisions from action authorizations.

Passing these fixtures proves that the expected route contracts are internally coherent. It does not prove that a future router selected or executed them correctly.
