# Verification Scripts

Quick validation and regression helpers. Use these when reproducing bug fixes
or confirming data migrations without running the full pytest suite.

Common patterns:
- `check_*` for lightweight sanity checks
- `verify_*` for replaying historic extraction scenarios
- `validate_*` for asserting invariants across cached artifacts
