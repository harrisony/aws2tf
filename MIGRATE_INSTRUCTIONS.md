# Migrating a Service to AWSResourceHandler

Each AWS service is migrated by creating a single file in `code/handlers/<service>.py` that
replaces two old files:

- `code/get_aws_resources/aws_<service>.py` — discovery (calling AWS APIs)
- `code/fixtf_aws_resources/fixtf_<service>.py` — HCL transformation

---

## Step 1 — Create `code/handlers/<service>.py`

### File skeleton

```python
"""
<Service> resource handlers — discovery and HCL transformation.

Replaces:
  code/get_aws_resources/aws_<service>.py
  code/fixtf_aws_resources/fixtf_<service>.py
"""

from __future__ import annotations
import logging
import boto3
import common
import context
from resource_registry import DefaultResourceHandler, register

log = logging.getLogger("aws2tf")


class MyResourceHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_my_resource",
            clfn="myservice",          # boto3 client name
            descfn="list_my_resources", # boto3 list/describe method
            topkey="MyResources",       # top-level key in response
            key="MyResourceId",         # field that holds the resource ID
            filterid="MyResourceId",    # filter param for single-resource lookup
        )

    def discover(self, resource_id: str | None) -> bool:
        # If id is None: discover all. Otherwise discover one.
        # Call common.write_import() for each found resource.
        # Call common.add_known_dependancy() / common.add_dependancy() as needed.
        # Mark completion: context.rproc[f"{self.terraform_type}.{id}"] = True
        ...
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        # Inspect attr_name / attr_value and rewrite line or set skip=1.
        # Call common.add_dependancy() when creating cross-resource references.
        return skip, line, flag1, flag2


register(MyResourceHandler())
```

### Rules for `discover()`

- Migrated from `get_aws_<service>.get_aws_<tf_type>()`.
- Remove the boilerplate debug log at the top of every old function (`"--> In X doing type=Y"`) — it adds noise and `log.debug()` calls around the real logic replace it where genuinely useful.
- Replace `str(inspect.currentframe().f_code.co_name)` in `handle_error()` calls with a plain string of the class method name, e.g. `"MyResourceHandler.discover"`.
- Replace string concatenation in `log` calls with `%`-formatting: `log.debug("found %s", name)`.
- Keep all logic identical — do not change what gets imported or what dependencies get added.
- If the old file had a `_old` function (e.g. `get_aws_lambda_function_old`), skip it — it is dead code.
- If two functions share the same name (Python uses the last definition), only migrate the last one.

### Rules for `transform()`

- Migrated from `fixtf_<service>.<tf_type>()`.
- Resources handled only by `__getattr__` / `BaseResourceHandler.default_handler` in the old file need **no `transform()` override** — `DefaultResourceHandler.transform()` is already a pass-through.
- The `flag1` and `flag2` parameters carry state between successive attribute lines for the same resource. Preserve any state-machine logic that uses them.
- `fixtf.globals_replace()` and `fixtf.deref_array()` are still available — import `fixtf` and call them directly.
- `BaseResourceHandler` static utilities (`skip_if_null`, `skip_if_zero`, `add_resource_reference`, `sanitize_resource_name`, etc.) are available via `from fixtf_aws_resources.base_handler import BaseResourceHandler`.

---

## Step 2 — Register at startup

Open `code/handlers/__init__.py` and add one import line:

```python
from handlers import myservice  # noqa: F401
```

The `register()` calls at the bottom of your handler file run automatically when the module is imported.

---

## Step 3 — Type-check

```bash
mise exec -- ty check code/handlers/myservice.py
```

Fix any errors before committing. Common issues:
- `context` variables inferred as `Literal` types — add an explicit annotation in `context.py` (e.g. `my_flag: bool = False`).
- Missing `| None` on `resource_id` parameter — the base class signature requires `str | None`.

---

## Step 4 — Commit and delete the old files in one commit

```bash
git rm code/get_aws_resources/aws_<service>.py \
       code/fixtf_aws_resources/fixtf_<service>.py
git add code/handlers/<service>.py code/handlers/__init__.py
git commit -m "feat: migrate <service> to AWSResourceHandler"
```

Always include the deletion in the same commit as the new handler.

---

## Reference — what the old files look like vs. the new

| Old | New |
|-----|-----|
| `get_aws_resources/aws_ec2.py` | `handlers/ec2.py` |
| `fixtf_aws_resources/fixtf_ec2.py` | same file |
| `get_aws_<type>(type, id, clfn, ...)` | `MyHandler.discover(resource_id)` |
| `aws_<type>(t1, tt1, tt2, flag1, flag2)` | `MyHandler.transform(line, attr_name, attr_value, flag1, flag2)` |
| Module registry in `fixtf.py` | `resource_registry` populated at startup |
| Module registry in `common.py` | same |

## Reference — already migrated

| Service | Handler file |
|---------|-------------|
| Lambda | `code/handlers/lambda_.py` |
| IAM | `code/handlers/iam.py` |
| S3 | `code/handlers/s3.py` |
