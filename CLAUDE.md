# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

**aws2tf** is a Python tool that imports existing AWS infrastructure into Terraform by:
1. Discovering AWS resources via boto3
2. Generating Terraform HCL `.tf` files and state
3. De-referencing hardcoded values (IDs, ARNs, regions, accounts) into Terraform resource references
4. Iteratively importing dependent resources until the graph is complete
5. Validating with `terraform plan`

## Commands

```bash
# Run the tool
./aws2tf.py -h               # Help
./aws2tf.py -t vpc           # Import all VPCs (and dependencies)
./aws2tf.py -t aws_vpc -i vpc-xxxx  # Import specific resource

# Lint
ruff check .

# Tests
pip install -r requirements-test.txt
pytest                       # All 267 tests
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest --cov=code --cov=aws2tf --cov-report=html  # With coverage
```

## Architecture

### Execution Flow (10 Phases in `aws2tf.py`)
1. Parse & validate CLI arguments
2. Setup environment and context
3. Setup workspace + `terraform init`
4. Handle merge mode (`-m` flag)
5. **Build resource lists** — parallel discovery of VPCs, subnets, SGs, Lambda, S3, etc.
6. **Process requested resource types** (user-specified via `-t`)
7. **Process known dependencies** (parent resources)
8. **Process detected dependencies** — iterative until no new refs found (typically 2–4 passes)
9. Validate + import (`terraform import`, `terraform plan`)
10. Finalize and cleanup

### Key Modules

| File | Role |
|------|------|
| `aws2tf.py` | Main orchestrator (~1,400 lines) |
| `code/common.py` | Shared utilities, `write_import()`, `add_dependancy()`, `rc()` (~3,500 lines) |
| `code/context.py` | Global application state (region, discovered resources, flags) |
| `code/resources.py` | Maps short codes (`vpc`, `efs`) and full names to Terraform resource types |
| `code/build_lists.py` | Parallel resource discovery via `ThreadPoolExecutor` |
| `code/fixtf.py` | Line-by-line transformation of generated `.tf` files (~1,400 lines) |
| `code/stacks.py` | CloudFormation stack import (~1,600 lines) |
| `code/get_aws_resources/` | 108 AWS service files — each calls boto3 to list/describe resources |
| `code/fixtf_aws_resources/` | 259 handler files — transform individual resource attributes |

### The Handler System (`code/fixtf_aws_resources/`)

The December 2024 optimization reduced handler boilerplate by 86% using Python's `__getattr__` pattern:

- **`base_handler.py`** — Provides 8 common utilities: `skip_if_zero()`, `skip_if_null()`, `skip_if_empty_array()`, `skip_fields()`, `add_resource_reference()`, `add_lifecycle_ignore()`, `sanitize_resource_name()`, `skip_if_empty_string()`
- **86% of resources** use the default handler (no custom logic needed)
- **14% of resources** (the `fixtf_*.py` files) have custom logic

Handler function signature:
```python
def aws_some_resource(t1, tt1, tt2, flag1, flag2):
    # t1: current line being processed
    # tt1: attribute name, tt2: attribute value
    # return skip=1 to exclude line, skip=0 to include
    return skip, t1, flag1, flag2
```

- **`aws_dict.py`** — Central registry mapping all 1,612 Terraform AWS resources to their boto3 client, API method, response key, and resource ID field

### Adding a New Resource

When adding support for a new AWS resource type:
1. Add the boto3 API caller in `code/get_aws_resources/aws_<service>.py`
2. Add/update the handler in `code/fixtf_aws_resources/fixtf_<service>.py` (only needed for non-default behavior)
3. Register in `code/fixtf_aws_resources/aws_dict.py`
4. Add type mapping in `code/resources.py` if a short code is desired
5. See `.kiro/steering/new-resource-testing.md` for testing guidance

### Dependency Tracking

Dependencies are tracked via `common.add_dependancy()`, called from handlers when an attribute references another resource. The main loop in `aws2tf.py` iterates until `context.rdep` (pending deps) is empty, reading generated `.tf` files to extract references each pass. Processed resources are tracked in `context.rproc` to prevent reprocessing.

### Output

Generated files land in `generated/tf.<account-id>.<region>/` — one `.tf` file per resource type by default, or merged into one file with `-s`.

## Runtime Requirements

- Python 3.12+
- boto3 >= 1.42.16
- Terraform >= v1.12.0
- AWS credentials configured (checked at startup)
