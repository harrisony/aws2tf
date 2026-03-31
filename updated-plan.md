# Modernisation Plan: aws2tf

## Context

aws2tf currently splits each AWS resource type across **two separate files and two separate patterns**:
- `code/get_aws_resources/aws_<service>.py` — discovers resources via boto3 and writes import blocks
- `code/fixtf_aws_resources/fixtf_<service>.py` — transforms HCL attribute lines line-by-line

These are two sides of the same coin (handling one resource type) but have no shared contract, resulting in ~350 files, duplicated boilerplate, and no way to know whether a resource type is fully implemented without checking two places. The goal is to replace both with a single interface that every resource type implements.

---

## The Interface

Define a Python ABC in `code/resource_handler.py`:

```python
from abc import ABC, abstractmethod

class AWSResourceHandler(ABC):

    @property
    @abstractmethod
    def terraform_type(self) -> str:
        """The Terraform resource type. E.g. 'aws_lambda_function'"""
        ...

    @abstractmethod
    def discover(self, resource_id: str | None) -> bool:
        """
        Discover resource(s) and write terraform import blocks.
        - If resource_id is None: discover all resources of this type.
        - If resource_id is given: discover that specific resource.
        Returns True if at least one resource was found.
        Replaces: get_aws_<service>.get_aws_<type>()
        """
        ...

    @abstractmethod
    def transform(
        self,
        line: str,
        attr_name: str,
        attr_value: str,
        flag1: bool,
        flag2: str,
    ) -> tuple[int, str, bool, str]:
        """
        Transform a single HCL attribute line.
        Returns (skip, modified_line, flag1, flag2).
        skip=1 omits the line; skip=0 writes it.
        Replaces: fixtf_<service>.<terraform_type>()
        """
        ...
```

This is the complete contract. Every resource type — all 1,612 of them — implements this interface.

---

## Concrete Implementations

### DefaultResourceHandler — covers ~86% of resource types

```python
class DefaultResourceHandler(AWSResourceHandler):
    """
    Generic handler for resources that need no custom logic.
    Drives discovery from aws_dict metadata.
    Passes all HCL attributes through unchanged.
    """

    def __init__(self, terraform_type: str, boto3_service: str,
                 list_op: str, response_key: str, id_field: str):
        self._terraform_type = terraform_type
        self._boto3_service = boto3_service
        ...

    @property
    def terraform_type(self) -> str:
        return self._terraform_type

    def discover(self, resource_id: str | None) -> bool:
        # Generic pagination + write_import() logic
        # (replaces getresource() in common.py)
        ...

    def transform(self, line, attr_name, attr_value, flag1, flag2):
        return 0, line, flag1, flag2  # pass-through
```

Instances for the 86% default case are auto-generated from `aws_dict.py` at startup — no new files needed.

### Custom handlers — the remaining ~14%

Each lives in `code/handlers/<service>.py` and only overrides what differs:

```python
# code/handlers/lambda_.py
class LambdaFunctionHandler(DefaultResourceHandler):

    def discover(self, resource_id):
        # Custom: download zip, add alias/permission dependencies
        ...

    def transform(self, line, attr_name, attr_value, flag1, flag2):
        if attr_name == "role":
            role_name = attr_value.split("/")[-1]
            common.add_dependancy("aws_iam_role", role_name)
            return 0, f'  role = aws_iam_role.{role_name}.arn\n', flag1, flag2
        if attr_name in ("filename", "source_code_hash", "last_modified"):
            return 1, line, flag1, flag2
        return super().transform(line, attr_name, attr_value, flag1, flag2)
```

`BaseResourceHandler`'s existing static utilities (`skip_if_null`, `add_resource_reference`, etc.) stay — they become helper methods called inside `transform()`.

---

## The Registry

Replace `FIXTF_MODULES` (in `fixtf.py`) and `AWS_RESOURCE_MODULES` (in `common.py`) with a single registry:

```python
# code/resource_registry.py
_registry: dict[str, AWSResourceHandler] = {}

def register(handler: AWSResourceHandler) -> None:
    _registry[handler.terraform_type] = handler

def get(terraform_type: str) -> AWSResourceHandler | None:
    return _registry.get(terraform_type)
```

Populated at startup from:
1. `aws_dict.py` metadata → auto-instantiate `DefaultResourceHandler` for each entry
2. Explicit imports of custom handler files (only ~14% of resource types)

---

## Migration Plan

### Phase 1: Fix Active Bugs (do first, unrelated to the refactor)

| Bug | File | Line | Fix |
|-----|------|------|-----|
| Invalid file mode `"e"` | `fixtf.py` | 770 | Change to `"r"` |
| `type` builtin shadowed | `fixtf.py` | 766 | Change to `ttft` |
| `exit_aws2tf` always-true condition | `context.py` | 140 | Change `or` to `and` |
| Both branches of `exit_aws2tf` identical | `context.py` | 143–146 | Remove dead branch |

### Phase 2: Define the Interface and Registry

1. Create `code/resource_handler.py` — the ABC above
2. Create `code/resource_registry.py` — the registry above
3. Create `code/handlers/` directory for custom handler implementations
4. Implement `DefaultResourceHandler` driven by `aws_dict.py`
5. Registry is populated at import time; `common.py` and `fixtf.py` remain unchanged in Phase 2

### Phase 3: Migrate Discovery (`get_aws_resources/` → `discover()`)

- For each service file in `get_aws_resources/`, extract each function into a handler's `discover()` method
- Start with the most-used: `ec2`, `lambda`, `s3`, `iam`, `rds`
- Update `common.call_resource()` to check the registry first, fall back to old module lookup
- Delete service files as each is migrated; old and new can coexist during migration

### Phase 4: Migrate Transformation (`fixtf_aws_resources/fixtf_*.py` → `transform()`)

- For each `fixtf_<service>.py`, extract each handler function into its handler class's `transform()` method
- Resources that used `__getattr__` default handling → no new code, `DefaultResourceHandler.transform()` is the default
- Update `fixtf.py` main loop to call `registry.get(ttft).transform(...)` instead of `FIXTF_MODULES` lookup
- Delete `fixtf_*.py` files as each service is migrated

### Phase 5: Collapse Prescan Loops in `fixtf.py`

The 7 sequential prescan loops (lines 492–615) should move into a `prescan()` method on the interface:

```python
def prescan(self, lines: list[str]) -> None:
    """Optional: inspect full file before line-by-line transform. Default: no-op."""
    pass
```

Resources like `aws_elasticache_cluster`, `aws_lb`, `aws_kinesis_firehose_delivery_stream` override this to set their flags. Eliminates the cascade of `if ttft == "..."` blocks.

### Phase 6: Cleanup

- Delete `code/get_aws_resources/` (fully replaced by `discover()` methods)
- Delete `code/fixtf_aws_resources/fixtf_*.py` (fully replaced by `transform()` methods)
- Delete the 220-line import block + `FIXTF_MODULES` dict in `fixtf.py` (replaced by registry)
- Delete `AWS_RESOURCE_MODULES` dict in `common.py` (replaced by registry)
- `aws_dict.py` and `base_handler.py` stay — they become inputs to the default handler

---

## Files After Migration

| Before | After |
|--------|-------|
| `code/get_aws_resources/` (108 files) | Deleted |
| `code/fixtf_aws_resources/fixtf_*.py` (201 files) | Deleted |
| `code/fixtf_aws_resources/base_handler.py` | Kept (utilities) |
| `code/fixtf_aws_resources/aws_dict.py` | Kept (metadata) |
| `code/fixtf_aws_resources/aws_common.py` | Kept (cross-resource transforms) |
| `code/fixtf.py` (220-line import block) | Simplified to registry lookup |
| `code/common.py` (`AWS_RESOURCE_MODULES` dict) | Simplified to registry lookup |
| **`code/resource_handler.py`** (new) | ABC definition |
| **`code/resource_registry.py`** (new) | Registry |
| **`code/handlers/<service>.py`** (new, ~20 files) | Custom handler implementations |

Net result: ~309 files deleted, ~22 files added. The ~86% default-case resources require zero new code — they get a `DefaultResourceHandler` instance from `aws_dict.py` metadata automatically.

---

## Verification

- `pytest` before and after each phase — zero regressions
- Smoke test `./aws2tf.py -t vpc`, `./aws2tf.py -t lambda`, `./aws2tf.py -t s3` against a real or localstack AWS account after each phase
- `mypy code/resource_handler.py code/resource_registry.py` — no errors
- `ruff check .` — no warnings
